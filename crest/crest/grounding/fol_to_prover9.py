"""FOL grounder (Phase 1.4) -- Prover9, not Z3.

Decision (2026-07-16): Logic-LM's own FOLIO grounding code uses Prover9 via
NLTK, not Z3 (see models/symbolic_solvers/... in teacherpeterpan/Logic-LLM --
its z3_solver module targets a different custom DSL for AR-LSAT/LogicalDeduction,
not FOLIO's raw FOL notation). FOLIO's own gold-FOL labels were themselves
verified with Prover9. Using Prover9 here keeps ceiling-accuracy numbers
directly comparable to both of those precedents. See
docs/MASTER_PLAN.md Phase 2 for why the *same* solver must be used for both
the ceiling check and the main experimental pipeline -- mixing solvers
between phases would defeat the point of the ceiling gate.

Windows can't execute the vendored Prover9 binary directly (it's a Linux
ELF), so `WSLProver9` below overrides NLTK's subprocess call to route
through `wsl -d Ubuntu -- ...` instead. This means every teammate running
this grounder on Windows needs WSL (Ubuntu) enabled -- document this
alongside the CUDA/HF setup steps, it's a genuine team-wide setup
requirement, not just this machine's quirk.

Added 2026-07-24 (Phase 3.1): GPU work (LlamaHarness translation) runs on
Kaggle, which is Linux, so the WSL wrapper doesn't apply there -- `LinuxProver9`
runs the same vendored binary directly instead. `get_prover9()` picks the
right one for the current OS at call time; `check_entailment` always goes
through it rather than hardcoding either class.
"""

import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from nltk.inference.prover9 import Prover9, Prover9Command, Prover9FatalException, Prover9LimitExceededException
from nltk.sem.logic import Expression

# Path to the vendored Linux prover9 binary, as seen from *inside* WSL.
_VENDOR_BIN = Path(__file__).resolve().parents[2] / "vendor" / "prover9" / "bin" / "prover9"
WSL_PROVER9_PATH = "/mnt/" + str(_VENDOR_BIN).replace(":", "").replace("\\", "/").lower()
WSL_DISTRO = "Ubuntu"

# FOLIO's raw Unicode FOL notation -> NLTK's ASCII logic syntax.
# Order matters: do XOR expansion before the simple symbol substitutions,
# since XOR expansion needs to find '<->' balance parens.
SYMBOL_MAP = {
    "∀": "all ",
    "∃": "exists ",
    "∧": "&",
    "∨": "|",
    "¬": "-",
    "→": "->",
    "↔": "<->",
}


def _find_matching_close(text: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"Unbalanced parentheses from index {open_idx} in: {text}")


def _scan_term_right(text: str, pos: int) -> tuple:
    """Find the immediate FOL term starting at/after `pos` (skipping
    whitespace): either a parenthesized group, a predicate call
    `Name(args)`, or a bare atom, optionally negation-prefixed.
    """
    i = pos
    while i < len(text) and text[i].isspace():
        i += 1
    start = i
    if i < len(text) and text[i] == "¬":
        i += 1
        while i < len(text) and text[i].isspace():
            i += 1
    if i < len(text) and text[i] == "(":
        return start, _find_matching_close(text, i) + 1
    while i < len(text) and (text[i].isalnum() or text[i] == "_"):
        i += 1
    if i < len(text) and text[i] == "(":
        return start, _find_matching_close(text, i) + 1
    return start, i


def _scan_term_left(text: str, pos: int) -> tuple:
    """Find the immediate FOL term ending at/before `pos` (skipping
    whitespace going backward) -- mirror of `_scan_term_right`.
    """
    i = pos
    while i > 0 and text[i - 1].isspace():
        i -= 1
    end = i
    if i > 0 and text[i - 1] == ")":
        depth = 0
        j = i - 1
        while j >= 0:
            if text[j] == ")":
                depth += 1
            elif text[j] == "(":
                depth -= 1
                if depth == 0:
                    break
            j -= 1
        open_idx = j
        k = open_idx
        while k > 0 and (text[k - 1].isalnum() or text[k - 1] == "_"):
            k -= 1
        term_start = k if k < open_idx else open_idx
    else:
        j = i
        while j > 0 and (text[j - 1].isalnum() or text[j - 1] == "_"):
            j -= 1
        term_start = j
    m = term_start
    while m > 0 and text[m - 1].isspace():
        m -= 1
    if m > 0 and text[m - 1] == "¬":
        term_start = m - 1
    return term_start, end


def _expand_xor(text: str) -> str:
    """FOLIO uses '⊕' (XOR), which NLTK's logic parser has no primitive for.
    Rewrite the immediate left/right operands of each '⊕' as
    '-((left)<->(right))' -- found by scanning for the adjacent FOL term on
    each side, not by assuming '⊕' always sits inside its own dedicated
    enclosing parens. Confirmed 2026-07-18 (FOLIO example_id 1364) that it
    doesn't always: '... → Cute(rockie) ⊕ Skittish(rockie)' has no wrapping
    parens around the XOR at all.
    """
    while "⊕" in text:
        idx = text.index("⊕")
        left_start, left_end = _scan_term_left(text, idx)
        right_start, right_end = _scan_term_right(text, idx + 1)
        left = text[left_start:left_end].strip()
        right = text[right_start:right_end].strip()
        replacement = f"-(({left})<->({right}))"
        text = text[:left_start] + replacement + text[right_end:]
    return text


def normalize_fol(text: str) -> str:
    text = _expand_xor(text)
    for symbol, replacement in SYMBOL_MAP.items():
        text = text.replace(symbol, replacement)
    return text


def parse_fol(text: str) -> Expression:
    return Expression.fromstring(normalize_fol(text))


class _Prover9CommonMixin:
    """Shared logic between the Windows (WSL-wrapped) and Linux (native)
    Prover9 runners -- everything except the actual subprocess invocation in
    `_call`, which differs per platform. Splitting it out this way means the
    `prolog_style_variables` fix (below) and error-classification logic can't
    silently drift apart between the two paths.
    """

    def _call_prover9(self, input_str, args=None, verbose=False):
        args = args or []
        # Critical: without this, Prover9's default convention treats any
        # identifier starting with letters t-z as an implicitly-quantified
        # variable, not a constant. FOLIO's camelCase constants routinely
        # start with those letters (e.g. "unitedStatesCitizenship", starting
        # with 'u') and were silently getting corrupted into free variables,
        # producing wrong entailment results. Confirmed 2026-07-18 via
        # example_id 1410 -- "unitedStatesCitizenship" was clausified as a
        # bare variable "y". With prolog_style_variables, constants are safe
        # regardless of their first letter, and explicit quantifiers (all x,
        # exists y) still bind correctly since that's determined by the
        # explicit quantifier syntax, not the naming convention.
        updated_input_str = "set(prolog_style_variables).\n\n"
        if self._timeout > 0:
            updated_input_str += "assign(max_seconds, %d).\n\n" % self._timeout
        updated_input_str += input_str

        stdout, returncode = self._call(updated_input_str, None, args, verbose)

        if returncode not in [0, 2]:
            errormsgprefix = "%%ERROR:"
            errormsg = None
            if errormsgprefix in stdout:
                errormsg = stdout[stdout.index(errormsgprefix) :].strip()
            if returncode in [3, 4, 5, 6]:
                raise Prover9LimitExceededException(returncode, errormsg)
            else:
                raise Prover9FatalException(returncode, errormsg)
        return stdout, returncode

    def _run_subprocess(self, cmd, input_str, verbose=False):
        if verbose:
            print("Calling:", cmd)
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
        )
        stdout, _ = p.communicate(input=input_str.encode("utf-8"))
        # Prover9 (a decades-old C program) doesn't reliably round-trip
        # non-ASCII identifiers (confirmed 2026-07-18, e.g. "świątek") when
        # echoing them back in its own output -- decode leniently so that
        # cosmetic mangling in the echoed text doesn't crash the actual
        # proof result, which Prover9 computed correctly regardless.
        return stdout.decode("utf-8", errors="replace"), p.returncode


class WSLProver9(_Prover9CommonMixin, Prover9):
    """Routes NLTK's Prover9 subprocess calls through `wsl -d Ubuntu --`,
    since the vendored prover9 binary is a Linux ELF executable and this
    class is used when the calling process itself is Windows.
    """

    def __init__(self, timeout: int = 60, wsl_distro: str = WSL_DISTRO, wsl_binary_path: str = WSL_PROVER9_PATH):
        super().__init__(timeout)
        self._wsl_distro = wsl_distro
        self._wsl_binary_path = wsl_binary_path

    def _call(self, input_str, binary, args=None, verbose=False):
        cmd = ["wsl", "-d", self._wsl_distro, "--", self._wsl_binary_path] + (args or [])
        return self._run_subprocess(cmd, input_str, verbose)


class LinuxProver9(_Prover9CommonMixin, Prover9):
    """Runs the vendored Linux prover9 binary directly -- no WSL wrapper
    needed because the calling process is already Linux (e.g. a Kaggle
    kernel, which is where Phase 3+ translation work runs since it needs a
    GPU). Added 2026-07-24 for Phase 3.1: until now the grounder only ever
    ran on Windows (Phase 2.1's ceiling check is CPU-only and local), so
    this path was never needed. `git clone` doesn't preserve the execute
    bit reliably, so `chmod` it defensively rather than assume it's set.
    """

    def __init__(self, timeout: int = 60, binary_path: Path = _VENDOR_BIN):
        super().__init__(timeout)
        self._binary_path = binary_path
        mode = self._binary_path.stat().st_mode
        if not mode & 0o111:
            self._binary_path.chmod(mode | 0o111)

    def _call(self, input_str, binary, args=None, verbose=False):
        cmd = [str(self._binary_path)] + (args or [])
        return self._run_subprocess(cmd, input_str, verbose)


def get_prover9(timeout: int = 60):
    """Picks the right Prover9 runner for the current OS -- WSL-wrapped on
    Windows (dev machine), native on Linux (Kaggle). See module docstring:
    same solver either way, just a different way of invoking the same
    vendored binary, so results stay comparable across environments.
    """
    if platform.system() == "Windows":
        return WSLProver9(timeout=timeout)
    return LinuxProver9(timeout=timeout)


@dataclass
class EntailmentResult:
    label: str  # "True" / "False" / "Uncertain"
    proved_goal: bool
    proved_negation: bool
    goal_proof_output: str
    negation_proof_output: str


def check_entailment(premises: List[str], conclusion: str, timeout: int = 60) -> EntailmentResult:
    """Mirrors FOLIO's own label scheme: try to prove the conclusion, try to
    prove its negation, and call it "Uncertain" if neither succeeds within
    the timeout. Same solver, same procedure, used for both the Phase 2.1
    ceiling check and the main pipeline -- see module docstring.
    """
    assumptions = [parse_fol(p) for p in premises]
    goal = parse_fol(conclusion)
    negated_goal = Expression.fromstring(f"-({normalize_fol(conclusion)})")

    prover = get_prover9(timeout=timeout)

    def _try_prove(target):
        try:
            return prover._prove(target, assumptions)
        except Prover9LimitExceededException as e:
            # Timeout (or other resource limit) is not proved within budget --
            # genuinely inconclusive, not a crash. Contributes to "Uncertain"
            # rather than aborting the whole entailment check.
            return False, f"LIMIT_EXCEEDED: {e}"

    proved_goal, goal_output = _try_prove(goal)
    proved_negation, negation_output = _try_prove(negated_goal)

    if proved_goal and proved_negation:
        # Shouldn't happen with a consistent premise set -- flag it rather
        # than silently pick one, it means either the premises are
        # contradictory or there's a bug in this grounder.
        label = "Contradiction"
    elif proved_goal:
        label = "True"
    elif proved_negation:
        label = "False"
    else:
        label = "Uncertain"

    return EntailmentResult(
        label=label,
        proved_goal=proved_goal,
        proved_negation=proved_negation,
        goal_proof_output=goal_output,
        negation_proof_output=negation_output,
    )

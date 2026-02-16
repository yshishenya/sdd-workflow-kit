from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillInfo:
    name: str
    description: str
    rel_path: str


def _parse_frontmatter(skill_md: str) -> tuple[str, str]:
    lines = skill_md.splitlines()
    if not lines or lines[0].strip() != "---":
        return ("", "")
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return ("", "")
    fm = lines[1:end]
    name = ""
    desc = ""
    for line in fm:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k == "name":
            name = v
        elif k == "description":
            desc = v
    return (name, desc)


def list_skillpack_skills(skillpack_dir: Path) -> list[SkillInfo]:
    skills_root = skillpack_dir / "skills"
    out: list[SkillInfo] = []
    if not skills_root.exists():
        return out
    for skill_file in sorted(skills_root.rglob("SKILL.md")):
        if not skill_file.is_file():
            continue
        try:
            rel_dir = skill_file.parent.relative_to(skills_root)
        except Exception:
            rel_dir = Path(skill_file.parent.name)
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        name, desc = _parse_frontmatter(text)
        if not name:
            name = rel_dir.as_posix()
        out.append(
            SkillInfo(
                name=name,
                description=desc,
                rel_path=str(Path("skillpacks") / skillpack_dir.name / "skills" / rel_dir / "SKILL.md"),
            )
        )
    out.sort(key=lambda s: s.name.lower())
    return out


def import_codex_skills(*, kit_root: Path, pack_name: str, source_dir: Path) -> None:
    src = source_dir
    if not src.exists():
        raise FileNotFoundError(f"Source skills dir not found: {src}")
    dest = kit_root / "skillpacks" / pack_name / "skills"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, dirs_exist_ok=False)
    print(f"Imported skills: {src} -> {dest}")

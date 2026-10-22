"""Builds "Coalition Demands" into the local mod folder.

Coalitions take back what their members lost and nothing else:
- cd_return_conquests: peace treaty that gives the loser's conquered locations back to coalition members, or revives
  dead countries near the coalition (scripted_triggers/cd_triggers.txt says which locations).
  Each location given back takes off the antagonism its conquest added (biases/cd_antagonism.txt). Subjects made
  recently go back to their former overlord or free (on_subject_created/on_transfer_subject mark them).
- peace_humiliate: copied from the game with a potential that bars it from coalition wars.
- coalition (international organization): copied from the game;
  rivals of the target, hegemons near a hegemon target and the Emperor (for HRE members) stay in it and want to
  join it.
- on_action/cd_on_actions.txt: a coalition's war is led by its strongest member in it (set_war_leader).
- scope_country_can_join_coalition_against: copied from the game; rivals of the target and hegemons near a hegemon target may join without the opinion
  and antagonism it otherwise needs; countries under a truce with the target and antagonism above 100 may join (and stay in) a coalition more
  than twice as strong as the target.
- dissolve_coalition: copied from the game; the losing coalition drops 75% of its antagonism towards the winner.
- cb_coalition: copied from the game; members want their own cores back.
- Settings in the Community Mod Framework mod menu (scripted_effects/cdm_settings.txt, script_values/cdm_values.txt).
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
GAME = "E:/SteamLibrary/steamapps/common/Europa Universalis V/game"
OUT = os.path.expanduser("~/Documents/Paradox Interactive/Europa Universalis V/mod/coalition_demands")

# Rivals of the target, and hegemons near a hegemon target (scripted_triggers/cd_triggers.txt)
EAGER = "cd_eager_coalition_member = { TARGET = scope:target }"

# Changes to the game's own files: each old text must be there exactly once, so a patch that changed it stops the build
PATCHES = {
    "in_game/common/peace_treaties/humiliate.txt": [(
        "\tblocks_full_annexation = yes\n",
        "\tblocks_full_annexation = yes\n\n"
        "\tpotential = { # Coalition Demands: coalitions don't humiliate\n"
        "\t\tNOT = { scope:winner ?= { cd_coalition_member_against = { TARGET = scope:loser } } }\n"
        "\t}\n",
    )],
    "in_game/common/international_organizations/coalition.txt": [(
        "\tpromote_strongest_member_to_war_leader = yes\n",
        "\tpromote_strongest_member_to_war_leader = no # Coalition Demands: the mod picks the war leader (on_action)\n",
    ), (
        "\t\t\t\t\t\tantagonism = {\n"
        "\t\t\t\t\t\t\ttarget = scope:target\n"
        "\t\t\t\t\t\t\tvalue < 30\n"
        "\t\t\t\t\t\t}\n",
        "\t\t\t\t\t\tAND = { # Coalition Demands: rivals and near hegemons stay without antagonism\n"
        "\t\t\t\t\t\t\tantagonism = {\n"
        "\t\t\t\t\t\t\t\ttarget = scope:target\n"
        "\t\t\t\t\t\t\t\tvalue < 30\n"
        "\t\t\t\t\t\t\t}\n"
        f"\t\t\t\t\t\t\tNOT = {{ {EAGER} }}\n"
        "\t\t\t\t\t\t}\n",
    ), (
        "\t\t\t\t\t\thas_truce_with = scope:target\n",
        "\t\t\t\t\t\tAND = { # Coalition Demands: a truce doesn't force out a member there for its antagonism, if the coalition is twice as strong\n"
        "\t\t\t\t\t\t\thas_truce_with = scope:target\n"
        "\t\t\t\t\t\t\tNOT = { cd_truce_breaker = { TARGET = scope:target } }\n"
        "\t\t\t\t\t\t}\n",
    ), (
        "\tai_desire_to_join = {\n",
        "\tai_desire_to_join = {\n" + "".join(
            f"\t\tif = {{ # Coalition Demands\n"
            f"\t\t\tlimit = {{ {trigger} = {{ TARGET = scope:target }} }}\n"
            "\t\t\tadd = {\n"
            f"\t\t\t\tdesc = \"{desc}\"\n"
            "\t\t\t\tvalue = 50\n"
            "\t\t\t}\n"
            "\t\t}\n"
            for trigger, desc in [("cd_rival_of_target", "game_concept_rival"),
                                  ("cd_hegemon_near_hegemon_target", "game_concept_hegemon"),
                                  ("cd_emperor_for_hre_member", "game_concept_hre_emperor")]),
    )],
    "in_game/common/peace_treaties/dissolve_coalition.txt": [(
        "\teffect = {\n",
        "\teffect = {\n"
        "\t\tcd_dissolve_coalition_antagonism_effect = yes # Coalition Demands: the losers drop 75% of their antagonism\n",
    )],
    "in_game/common/casus_belli/coalition.txt": [(
        "\tai_cede_location_desire = -1000\n",
        "\tai_cede_location_desire = { # Coalition Demands: members want their own cores back (the game's Return Core treaty)\n"
        "\t\tvalue = -1000\n"
        "\t\tif = {\n"
        "\t\t\tlimit = { scope:location = { is_core_of = root } }\n"
        "\t\t\tvalue = 100\n"
        "\t\t}\n"
        "\t}\n",
    )],
    "in_game/common/scripted_triggers/international_organization_triggers.txt": [(
        "\topinion = {\n"
        "\t\ttarget = $target$\n"
        "\t\tvalue < -50\n"
        "\t}\n"
        "\n"
        "\twithin_diplomatic_range = $target$\n"
        "\tantagonism = {\n"
        "\t\ttarget = $target$\n"
        "\t\tvalue > 50\n"
        "\t}\n",
        "\twithin_diplomatic_range = $target$\n"
        "\tOR = { # Coalition Demands: rivals of the target and hegemons near a hegemon target join whatever their opinion and antagonism\n"
        "\t\tAND = {\n"
        "\t\t\topinion = {\n"
        "\t\t\t\ttarget = $target$\n"
        "\t\t\t\tvalue < -50\n"
        "\t\t\t}\n"
        "\t\t\tantagonism = {\n"
        "\t\t\t\ttarget = $target$\n"
        "\t\t\t\tvalue > 50\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t\tcd_eager_coalition_member = { TARGET = $target$ }\n"
        "\t}\n",
    ), (
        "\tnot = { has_truce_with = $target$ }\n",
        "\tOR = { # Coalition Demands: a truce doesn't keep out a country there for its antagonism, if the coalition is twice as strong\n"
        "\t\tnot = { has_truce_with = $target$ }\n"
        "\t\tcd_truce_breaker = { TARGET = $target$ }\n"
        "\t}\n",
    )],
}

LOC = {
    "english": {
        "cd_return_conquests": "Return Conquests",
        "cd_return_conquests_entry": "Return the conquered locations",
        "cd_return_conquests_entry_short": "$cd_return_conquests$",
        "cd_return_conquests_desc": "Locations taken from members of the coalition, and from countries near it, go back to them; countries destroyed near the coalition rise again; recent subjects go back to their former overlord or free.",
        "cd_return_conquests_tt": "Locations taken from coalition members and from countries near the coalition go back to them; locations of destroyed countries near the coalition restore those countries. Subjects made recently go back to the overlord they were taken from, or become free.",
        "cd_antagonism_returned_land": "Returned conquered locations",
        "cd_antagonism_freed_subject": "Freed subjects",
        "cd_tt_rival": "We chose the coalition's target as our [Concept('rival', 'rival')|e] (mod rule: those who chose the target as their rival)",
        "cd_tt_hegemon": "We are a [Concept('hegemon', 'hegemon')|e] near the hegemon target, with an [Concept('opinion', 'opinion')|e] of it below +150 (mod rule: hegemons against a hegemon)",
        "cd_tt_emperor": "We are the [Concept('hre_emperor', 'Emperor')|e], a member of the Empire is in the coalition, and our [Concept('opinion', 'opinion')|e] of its target is below +150 (mod rule)",
        "cd_tt_truce_rule": "The mod rule to ignore the truce is on",
        "cd_tt_truce_antagonism": "Our [Concept('antagonism', 'antagonism')|e] towards the target is above the mod setting \"Antagonism above\"",
        "cd_tt_truce_strength": "The coalition is stronger than its target by more than the mod setting \"Coalition stronger by\"",
        "cdm_name": "Coalition Demands",
        "cdm_desc": "Coalitions take back the locations you conquered from their members and neighbours instead of humiliating you.",
        "cdm__settings_name": "Settings",
        "cdm__settings__return_name": "Return of conquests",
        "cdm__settings__return_desc": "Which conquered locations a coalition demands back.",
        "cdm__return_years_name": "Years to demand back",
        "cdm__return_years_desc": "For how many years after a conquest a coalition can demand the location back. Locations already conquered keep the years set when they were taken: a change applies to new conquests only.",
        "cdm__return_core_name": "Not once it is our core",
        "cdm__return_core_desc": "A conquered location can no longer be demanded back once it becomes a core of its new owner, even before the years run out.",
        "cdm__return_noncore_name": "Also non-core locations",
        "cdm__return_noncore_desc": "Off: a country gets back only its cores. On: every location taken from it, cores or not (a revived country comes back with all its former locations).",
        "cdm__settings__truce_name": "Joining despite a truce",
        "cdm__settings__truce_desc": "Countries under a truce with the coalition's target, there for their antagonism. Rivals and hegemons always keep a truce.",
        "cdm__truce_join_name": "Ignore the truce",
        "cdm__truce_join_desc": "Countries under a truce may join (and stay in) a coalition when both conditions below hold.",
        "cdm__truce_antagonism_name": "Antagonism above",
        "cdm__truce_antagonism_desc": "Their antagonism towards the target must be above this. A coalition normally needs 50.",
        "cdm__truce_strength_name": "Coalition stronger by",
        "cdm__truce_strength_desc": "The coalition must be more than this many times as strong as its target, by the army comparison of the coalition window (total combat power).",
        "cdm__settings__join_name": "Others who may join",
        "cdm__settings__join_desc": "Countries that may join a coalition without the antagonism above 50 and the opinion below -50 it otherwise needs.",
        "cdm__hegemons_name": "Hegemons against a hegemon",
        "cdm__hegemons_desc": "A hegemon may join a coalition against a neighbouring hegemon if its opinion of it is below +150. Neighbouring: borders within 300 apart, as far as the AI joins coalitions at all.",
        "cdm__rivals_name": "Those who chose the target as their rival",
        "cdm__rivals_desc": "Countries that chose the coalition's target as their rival.",
        "cdm__emperor_name": "The Emperor, for the HRE",
        "cdm__emperor_desc": "The Holy Roman Emperor may join a coalition with a member of the Empire in it, if the Emperor's opinion of its target is below +150.",
        "cd_antagonism_coalition_dissolved": "Dissolved our coalition",
        "cd_dissolve_coalition_antagonism_tt": "Members of the coalition, and everyone who fought on its side, lose 75% of their antagonism towards the winner.",
    },
    "russian": {
        "cd_return_conquests": "Возврат завоёванного",
        "cd_return_conquests_entry": "Вернуть завоёванные районы",
        "cd_return_conquests_entry_short": "$cd_return_conquests$",
        "cd_return_conquests_desc": "Районы, отнятые у членов коалиции и у стран рядом с ней, возвращаются к ним, уничтоженные страны рядом с коалицией возрождаются, а недавние ленники возвращаются прежнему сюзерену или становятся независимыми.",
        "cd_return_conquests_tt": "Районы, отнятые у членов коалиции и у стран рядом с ней, возвращаются к ним; районы уничтоженных стран рядом с коалицией возрождают эти страны. Недавние ленники возвращаются сюзерену, у которого их отняли, или становятся независимыми.",
        "cd_antagonism_returned_land": "Вернули завоёванные районы",
        "cd_antagonism_freed_subject": "Освободили ленников",
        "cd_tt_rival": "Мы выбрали цель коалиции своим [Concept('rival', 'соперником')|e] (правило мода «Объявившие цель соперником»)",
        "cd_tt_hegemon": "Мы [Concept('hegemon', 'гегемон')|e] рядом с целью-гегемоном, наше [Concept('opinion', 'мнение')|e] о ней ниже +150 (правило мода «Гегемоны против гегемона»)",
        "cd_tt_emperor": "Мы [Concept('hre_emperor', 'император')|e], в коалиции есть член империи, наше [Concept('opinion', 'мнение')|e] о её цели ниже +150 (правило мода «Император за членов СРИ»)",
        "cd_tt_truce_rule": "Включено правило мода «Игнорировать перемирие»",
        "cd_tt_truce_antagonism": "Наша [Concept('antagonism', 'неприязнь')|e] к цели выше настройки мода «Неприязнь выше»",
        "cd_tt_truce_strength": "Коалиция сильнее цели больше, чем задано в настройке мода «Коалиция сильнее в»",
        "cdm_name": "Требования коалиций",
        "cdm_desc": "Коалиции требуют вернуть районы, завоёванные у их членов и соседей, а не унижают вас.",
        "cdm__settings_name": "Настройки",
        "cdm__settings__return_name": "Возврат завоёванного",
        "cdm__settings__return_desc": "Какие завоёванные районы коалиция требует вернуть.",
        "cdm__return_years_name": "Сколько лет можно требовать",
        "cdm__return_years_desc": "Сколько лет после завоевания коалиция может потребовать район обратно. Уже завоёванные районы следуют сроку, который действовал при их завоевании: изменение применится только к новым завоеваниям.",
        "cdm__return_core_name": "Не требовать, если район стал национальным",
        "cdm__return_core_desc": "Завоёванный район больше нельзя потребовать обратно, когда он стал национальным для нового владельца, даже если срок не вышел.",
        "cdm__return_noncore_name": "Возвращать и ненациональные районы",
        "cdm__return_noncore_desc": "Выключено: стране возвращаются только её национальные районы. Включено: все районы, которые у неё отняли, национальные и остальные (воссозданная страна получает все свои прежние районы).",
        "cdm__settings__truce_name": "Вступление вопреки перемирию",
        "cdm__settings__truce_desc": "Страны с перемирием с целью коалиции, вступающие из-за неприязни. Соперники и гегемоны перемирие всегда соблюдают.",
        "cdm__truce_join_name": "Игнорировать перемирие",
        "cdm__truce_join_desc": "Страны с перемирием могут вступить в коалицию и остаться в ней, если выполнены оба условия ниже.",
        "cdm__truce_antagonism_name": "Неприязнь выше",
        "cdm__truce_antagonism_desc": "Их неприязнь к цели должна быть выше этого значения. Обычно для коалиции нужно 50.",
        "cdm__truce_strength_name": "Коалиция сильнее в",
        "cdm__truce_strength_desc": "Коалиция должна быть сильнее цели больше чем во столько раз — по сравнению армий в окне коалиции («Всего боевой мощи»).",
        "cdm__settings__join_name": "Кто ещё может вступать",
        "cdm__settings__join_desc": "Страны, которые могут вступить в коалицию без обычно нужных неприязни выше 50 и мнения ниже −50.",
        "cdm__hegemons_name": "Гегемоны против гегемона",
        "cdm__hegemons_desc": "Гегемон может вступить в коалицию против соседнего гегемона, если мнение о нём ниже +150. Соседний: границы не дальше 300 друг от друга — дальше ИИ в коалиции вообще не вступает.",
        "cdm__rivals_name": "Объявившие цель соперником",
        "cdm__rivals_desc": "Страны, которые выбрали цель коалиции своим соперником.",
        "cdm__emperor_name": "Император за членов СРИ",
        "cdm__emperor_desc": "Император Священной Римской империи может вступить в коалицию, в которой есть член империи, если его мнение о цели коалиции ниже +150.",
        "cd_antagonism_coalition_dissolved": "Распустили нашу коалицию",
        "cd_dissolve_coalition_antagonism_tt": "Члены коалиции и все, кто воевал на её стороне, теряют 75% неприязни к победителю.",
    },
}
COMMON = {  # flag names the Community Mod Framework looks up
    "cdm__return_years": "cdm__return_years", "cdm__return_core": "cdm__return_core", "cdm__return_noncore": "cdm__return_noncore",
    "cdm__truce_join": "cdm__truce_join", "cdm__truce_antagonism": "cdm__truce_antagonism",
    "cdm__truce_strength": "cdm__truce_strength", "cdm__hegemons": "cdm__hegemons", "cdm__rivals": "cdm__rivals", "cdm__emperor": "cdm__emperor",
}
LANGS = ["english", "french", "german", "spanish", "polish", "russian", "japanese", "korean", "simp_chinese", "braz_por", "turkish"]


def write(path, text):
    full = os.path.join(OUT, *path.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8-sig", newline="\n") as fh:
        fh.write(text)


def patched(path):
    with open(os.path.join(GAME, path), encoding="utf-8-sig") as fh:
        text = fh.read().replace("\r\n", "\n")
    for old, new in PATCHES[path]:
        if text.count(old) != 1:
            raise SystemExit(f"{path} changed in the game: check the patch before building")
        text = text.replace(old, new)
    return text


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for folder, _, files in os.walk(SRC):
        for name in files:
            src = os.path.join(folder, name)
            with open(src, encoding="utf-8-sig") as fh:
                write(os.path.relpath(src, SRC).replace(os.sep, "/"), fh.read())
    for path in PATCHES:
        write(path, patched(path))
    for lang in LANGS:
        lines = dict(LOC.get(lang, LOC["english"]), **COMMON)
        write(f"main_menu/localization/{lang}/cd_l_{lang}.yml",
              f"l_{lang}:\n" + "".join(f' {k}: "{v}"\n' for k, v in lines.items()))
    meta = {"name": "Coalition Demands [LOCAL]", "id": "grackbox.coalition_demands", "version": "0.1.0", "game_id": "eu5",
            "supported_game_version": "1.4.*",
            "short_description": "Coalitions take back the locations you conquered from their members instead of humiliating you.",
            "tags": ["Diplomacy", "1.4"],
            "relationships": [{"rel_type": "dependency", "id": "community_mod_framework", "display_name": "Community Mod Framework",
                               "resource_type": "mod", "version": "2.*"}],
            "game_custom_data": {}}
    write(".metadata/metadata.json", json.dumps(meta, indent=4, ensure_ascii=False) + "\n")
    shutil.copyfile(os.path.join(HERE, "cover.png"), os.path.join(OUT, ".metadata", "thumbnail.png"))
    print("built ->", OUT)


if __name__ == "__main__":
    main()

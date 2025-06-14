import streamlit as st
import os
import json
import random


THEMES = {
    "Scandal & Betrayal": [
        {
            "name": "Cheaters’ Chateau",
            "desc": "Suspicious lovers spy on their partners in a gaudy mansion rigged with hidden cams catching every sneaky grope and motel rendezvous. Maury-style confrontations erupt in a velvet-draped 'truth dungeon,' where lie detectors buzz and betrayed exes hurl whipped cream pies. The finale pits cheaters against their jilted lovers in a mud-wrestling 'trust rebuild' that always ends in tears and tangles."
        },
        {
            "name": "Backstab Beach",
            "desc": "Besties turned enemies vacation in a tacky seaside villa, plotting revenge via raunchy pranks like spiking mojitos with hot sauce or swapping sunscreen for mayonnaise. Challenges include 'expose your ex' karaoke battles and blindfolded 'who’s my sidepiece' guessing games. The winner gets a yacht party; losers get their sexts projected on a Jumbotron for the boardwalk to judge."
        },
        {
            "name": "Ricki’s Ratchet Revelations",
            "desc": "Ricki Lake hosts a talk show where feuding couples air their nastiest laundry—think foot-fetish betrayals and stolen sex tapes—in front of a jeering crowd. DNA tests and 'who’s the side chick' quizzes spark chair-throwing chaos. Winners get a tacky couples’ retreat; losers slink off to a 'shame cam' confessional where Ricki roasts their bad wigs and worse choices."
        },
        {
            "name": "Swipe Right to Spite",
            "desc": "Jilted singles join a dating app rigged to match them with their exes’ new flings, sparking hookups and havoc in a neon-lit loft. Dates involve body-shot relays and 'spill the tea' truth booths where secrets like funky hygiene or secret kinks get aired. The finale is a 'burn or bang' ceremony where players choose revenge or reconciliation, usually with flying martinis."
        },
        {
            "name": "Judge Judy’s Jilted Justice",
            "desc": "Judge Judy tears into cheating exes suing over trashed thongs, pawned promise rings, and leaked OnlyFans clips. Her courtroom’s a circus of sweaty defendants and plaintiffs flashing tacky tattoos as evidence. Judy’s rulings come with savage one-liners, and losers must post groveling apologies on X while winners get petty cash and bragging rights."
        }
    ],
    "Freaky Competitions": [
        {
            "name": "Slime & Grind",
            "desc": "Contestants in skimpy unitards slog through goo-filled obstacle courses—think chocolate syrup slides and whipped-cream pits—while dodging vibrating 'penalty probes.' Winners get a cash prize and a golden dildo trophy; losers take a slime shower while the crowd chants 'lube it up!' Hosted by a cackling drag queen who spikes the drama with X polls."
        },
        {
            "name": "Kink or Cringe",
            "desc": "Kooky couples compete in risqué challenges like blindfolded whipped-cream sculpting and 'guess the fetish' charades, judged by a panel of adult film stars. Points for boldness, deductions for awkwardness. The finale is a 'bedroom Olympics' with events like edible-panty relay races. Winners get a spicy toy chest; losers get a cringe compilation aired on X."
        },
        {
            "name": "Puke & Plunge",
            "desc": "Gnarly daredevils tackle gross-out gauntlets: chugging curdled milkshakes, diving into dumpster-juice pools, and wrestling in rancid fish guts. Pukers get penalty points; survivors earn 'gut glory.' Hosted by a Maury-esque hype man who screams 'You are NOT the toughest!' at quitters. Top prize is cash and a stomach pump voucher."
        },
        {
            "name": "Strip Trivia Takedown",
            "desc": "Buzzed contestants answer raunchy trivia—think sex toy history or porn star aliases—while shedding clothes for wrong answers. The stage is a neon-lit strip club, complete with heckling 'hype hoes.' Last one standing (or least naked) wins a Vegas bacchanal; losers streak through a foam party gauntlet as penance."
        },
        {
            "name": "Fetish Feud",
            "desc": "Rival kink clans battle in a Family Feud-style showdown, guessing the top answers to prompts like 'What’s the weirdest place to get freaky?' or 'Name a bedroom toy you’d hide from your mom.' Wrong answers trigger a 'spank tank' dunk. Hosted by Ricki Lake, who stirs the pot with shady side-eyes. Winners get a dungeon makeover."
        }
    ],
    "Dysfunction Junction": [
        {
            "name": "Trailer Park Telenovela",
            "desc": "Feuding redneck clans share a muddy lot, stirring drama over stolen moonshine, loud late-night hookups, and who let the pitbull eat the Spam. Cameras catch every mullet flip and beer-can toss. Weekly 'family meetings' with a Ricki-style mediator end in screaming matches or sloppy makeouts. The season ends with a demolition-derby wedding."
        },
        {
            "name": "Hoarder Heartbreak",
            "desc": "Messy packrats and their fed-up partners live in a junk-filled warehouse, tasked with decluttering while airing grudges over moldy sex toys and crusty takeout boxes. Maury hosts therapy sessions that spiral into 'who kept the used condoms' fights. The cleanest couple wins a new trailer; the filthiest gets shamed on a landfill catwalk."
        },
        {
            "name": "Polyamory Pile-Up",
            "desc": "Throuples and moresomes navigate jealousy and bed-hogging in a tacky commune, with challenges like 'who gets the middle spoon' negotiations and group twerk-offs. Hidden cams catch sneaky solo hookups, sparking Maury-level meltdowns. The most 'harmonious' polycule wins a tantric retreat; the messiest gets a public breakup roast."
        },
        {
            "name": "Mama’s Boy Meltdown",
            "desc": "Clingy sons and their overbearing moms face off against fed-up girlfriends in a kitschy suburban ranch. Tasks like 'cut the cord' cooking contests and 'whose side are you on' lie detectors fuel shrieking tantrums. Judge Judy guest-stars to slap sense into mama’s boys. Winners get a couples’ getaway; losers get matching ankle monitors."
        },
        {
            "name": "Sibling Sh*tshow",
            "desc": "Warring brothers and sisters share a grimy loft, reigniting childhood grudges over who got the bigger burger or stole whose bong. Challenges include 'petty payback' prank wars and 'who’s mom’s favorite' quizzes. Ricki mediates, but it’s all chair-throwing chaos. The least dysfunctional sib wins a cash stash; others get a 'grow up' lecture on X."
        }
    ],
    "Shameless Fame Chasers": [
        {
            "name": "Clout Chasers’ Compound",
            "desc": "Wannabe influencers live in a blinged-out bunker, competing for X followers via stunts like bikini car washes and 'accidental' nip-slip livestreams. Challenges include viral lip-sync battles and 'shade your rival' diss tracks. The top clout king or queen gets a reality spinoff; flops get their accounts suspended live on air."
        },
        {
            "name": "OnlyFans Overdrive",
            "desc": "Aspiring adult-content creators share a seedy studio, hustling for subscribers with spicy photoshoots and 'fan request' dares like eating whipped cream off strangers. Rivalries spark over who’s got the best angles—or worst hygiene. The top earner gets a Vegas penthouse shoot; the bottom gets a 'career pivot' to foot modeling."
        },
        {
            "name": "Viral Vipers",
            "desc": "Attention-hungry randos stage outrageous pranks—think streaking at monster truck rallies or twerking in a funeral parlor—for X clout. Judges, including a snarky Judge Judy, rate their audacity. Top prankster wins a talent agency deal; flops get a 'cease and desist' and a public shaming by a Ricki Lake cameo."
        },
        {
            "name": "Hashtag Harem",
            "desc": "A D-list TikToker picks a ‘brand ambassador’ from a pool of thirsty clout-chasers in a gaudy influencer mansion. Contestants endure challenges like 'sell this sketchy diet tea' and 'fake a beach body glow-up.' Betrayals and blurry nudes leak faster than the Wi-Fi. The chosen one joins the TikToker’s entourage; rejects cry on X Live."
        },
        {
            "name": "Fame or Flop",
            "desc": "Deluded nobodies pitch atrocious talents—think armpit serenades or burping ASMR—to a panel of washed-up reality stars. Maury hosts, hyping the crowd to boo or throw marshmallows. The least cringe act gets a shady manager and a shot at D-list glory; the worst gets a 'talent autopsy' segment where Judy rips them apart."
        }
    ],
    "Grimy Makeovers": [
        {
            "name": "Glow-Up or Throw-Up",
            "desc": "Frumpy hot messes get raunchy makeovers—think vajazzling and spray-tan orgies—in a grimy salon run by a sassy drag queen. Challenges include strutting in knockoff stilettos and 'seduce the mirror' pole-dance routines. The best glow-up wins a boudoir photoshoot; the frumpiest gets a mud-mask humiliation on X."
        },
        {
            "name": "Tacky to Tasty",
            "desc": "Greasy slobs transform into ‘sexy’ via crash diets, teeth-whitening disasters, and spray-on abs, all in a strip-mall spa. Ricki hosts, forcing them to confront their crusty habits (like never washing their thongs). The hottest makeover wins a red-carpet cameo; the grossest gets a ‘hygiene bootcamp’ with Maury’s tough love."
        },
        {
            "name": "From Crusty to Lusty",
            "desc": "Unhygienic randos—think BO champs and toenail hoarders—compete for a full-body overhaul in a biohazard-grade clinic. Challenges include 'survive the waxing' and 'flirt without flinching.' Judge Judy guest-judges, gagging at their before pics. The sexiest wins a dating show slot; the crustiest gets a hazmat dunk tank."
        },
        {
            "name": "Bling My Bod",
            "desc": "Dowdy contestants get bedazzled into gaudy glory—think nipple piercings and glittery butt tattoos—in a seedy piercing parlor. Tasks include 'werk the runway' in edible lingerie and 'survive the tanning bed gauntlet.' The blingiest wins a Miami club appearance; the dullest gets a ‘sparkle intervention’ with Ricki’s shade."
        },
        {
            "name": "Squalor to Sizzling",
            "desc": "Filthy shut-ins trade their stained sweatpants for fishnets and fake lashes in a chaotic makeover bootcamp. Challenges like 'shave the unibrow' and 'master the twerk' spark meltdowns. Maury narrates, exposing their roach-infested pasts. The most sizzling wins a Vegas glow-up tour; the squalid get a public scrub-down shaming."
        }
    ],
    "Dramas": [
        {
            "name": "Meth Motels & Meltdowns",
            "desc": "Inspired by Breaking Bad, shady hustlers run a seedy motel chain, juggling side hustles like bootleg lube empires and knockoff Viagra rackets. Hidden cams catch backroom deals and sweaty hookups gone wrong. Maury hosts 'bust or betray' stings, exposing who snitched. The last kingpin standing wins a shady offshore account; busts face Judge Judy’s courtroom wrath."
        },
        {
            "name": "Blood, Sweat & Thongs",
            "desc": "Rival strip-club dynasties battle for neon-lit turf, slinging insults and pasties in a gritty underworld of pole-dance wars and VIP-room betrayals. Challenges include 'steal the headliner' sabotage and 'pimp the private room' scams. Ricki mediates explosive sit-downs that end in wig-pulling. The top club wins a Vegas franchise; losers get shamed on X."
        },
        {
            "name": "Cartel of Kink",
            "desc": "Leather-clad doms and subs run an underground fetish ring, dodging raids while competing for clients with wilder kinks—think whipped-cream wrestling or tickle-torture marathons. Double-crosses and stolen client lists spark Maury-level showdowns. The top 'dungeon boss' gets a secret penthouse; snitches face a public flogging reveal."
        },
        {
            "name": "Grindhouse Grudges",
            "desc": "Tattooed bouncers and bottle girls at a sleazy nightclub feud over tips, turf, and who’s banging the DJ. Tensions boil during 'last call' brawls and 'who runs the VIP' power plays. Judge Judy arbitrates disputes over stolen stilettos and bar-tab scams. The crew that rules the club wins a Miami pop-up; losers scrub the sticky floors."
        },
        {
            "name": "Pawn Shop Pacts",
            "desc": "Desperate pawnbrokers trade in shady goods—cursed sex dolls, haunted vibrators, and stolen wedding rings—while dodging cops and backstabbing kin. Deals go sour in a grimy shop where Ricki hosts 'truth or forfeit' appraisals, exposing fakes and felons. The slickest hustler wins a black-market empire; busts get a Maury-style lie detector roast."
        }
    ],
    "Comedies": [
        {
            "name": "Seinfeld’s Sleazy Sitcom",
            "desc": "A gang of neurotic randos—think a nympho Kramer and a chain-smoking Elaine—bicker over petty crap like who hogged the communal Fleshlight or whose BO cleared the diner. Episodes revolve around absurd scams, like faking an orgasm contest for clout. Ricki pops in as a sassy landlord, stirring the pot. The funniest gets a comedy club gig; flops get heckled on X."
        },
        {
            "name": "The Gutter Friends",
            "desc": "A raunchy spin on Friends, where six hot messes share a dive bar apartment, obsessing over who’s hooking up and who left pubes in the shower. Gags include 'the one with the edible thong heist' and 'the one where they all get crabs.' Maury hosts a reunion where they vote out the least sexy. Winners get a tacky loft; losers clean the bar’s grease traps."
        },
        {
            "name": "Curb Your Crankiness",
            "desc": "A Larry David-esque grump navigates a neon-lit slum, whining about loud orgies next door and roommates eating his expired yogurt. Misadventures include crashing a swinger’s party and starting a feud over a stolen butt plug. Judge Judy cameos as his fed-up neighbor, slapping him with fines. The least annoying wins a new pad; the worst gets evicted live."
        },
        {
            "name": "Two and a Half Hookups",
            "desc": "Two sleazy bros and a freeloading cousin crash in a beachside shack, chasing tail and botched get-rich schemes like selling knockoff lube. Laughs come from their disastrous pickup lines and fights over who gets the top bunk. Ricki guest-stars as a no-nonsense bartender. The smoothest player wins a Miami fling; flops wash dishes for a month."
        },
        {
            "name": "The Crass Office",
            "desc": "A mockumentary of a failing adult toy warehouse, where horny clerks and a pervy boss clash over who sold the defective dildos or clogged the break room sink with glitter lube. Pranks like swapping desks with sex dolls spark chaos. Maury hosts a 'team-building' roast where the top slacker wins a raise; the rest get demoted to janitor."
        }
    ]
}

# Map each category to an emoji
GENRE_EMOJIS = {
    "Scandal & Betrayal": "",
    "Freaky Competitions": "",
    "Dysfunction Junction": "",
    "Shameless Fame Chasers": "",
    "Grimy Makeovers": "",
    "Dramas": "",
    "Comedies": ""
}



CHARACTER_BEHAVIOR_TRAITS = [
    "Emotional", "Aggressive", "Comedic", "Scheming", "Shy", "Bold",
    "Unhinged", "Secretive", "Petty", "Obsessive", "Impulsive", "Naive"
]

RANDOM_NAMES = [
    "Bingo Spangles", "Kiki Sassafras", "Duke Danger", "Bubbles Malone",
    "Ricky Stankfoot", "Trisha Pickle", "Jazz Bazooka", "Fanny Magoo",
    "Terry Tinfoil", "Muffin Topps", "Lola Slinky", "Butters McGee"
]
CHARACTER_BEHAVIOR_TRAITS = [
    "Charismatic", "Scheming", "Loyal", "Impulsive", "Brooding", "Flamboyant", "Cold-blooded", "Eccentric",
    "Street-smart", "Bookish", "Benevolent", "Ruthless", "Mysterious", "Chill", "Ambitious", "Cunning",
    "Comedic", "Sensitive", "No-nonsense", "Wildcard", "Self-absorbed", "Stoic", "Reckless", "Zen",
    "Rich", "Poor", "Blue-collar", "Glamorous", "Grimy", "Influencer", "Has-been", "Bossy", "Introvert",
    "Extrovert", "Messy", "Put-together", "Petty", "Savage", "Unapologetic", "Try-hard", "Low-key",
    "Hustler", "Trust-fund", "Slacker", "Hacker", "Custom..."
]

RANDOM_NAMES = [
    "Bingo Spangles", "Kiki Sassafras", "Duke Danger", "Bubbles Malone",
    "Ricky Stankfoot", "Trisha Pickle", "Jazz Bazooka", "Fanny Magoo",
    "Terry Tinfoil", "Muffin Topps", "Lola Slinky", "Butters McGee"
]

PHYS_DESCS = [
    "Tall and sharp-eyed", "Short and quick-witted", "Average build, striking aura",
    "Built like a tank", "Slender and wiry", "Radiates mischief", "Glasses, neon hair",
    "Gold teeth flashing", "Face tattoos and wild piercings", "Always fidgeting",
    "Impossibly perfect hair", "Wearing sunglasses indoors"
]

FASHIONS = [
    "thrifted retro jackets and scuffed boots", "tailored Italian suits and diamond cufflinks",
    "hoodie-clad, laptop in tow", "designer athleisure and gold sneakers",
    "vintage band tee, wild hair, piercings everywhere", "minimalist black and silver",
    "cargo pants with more pockets than secrets", "90s rap video chic",
    "covered in fake fur and rhinestones", "fast fashion with maximum bling"
]

WEALTH = [
    "broke", "living large", "modest means", "secretly wealthy", "unapologetically rich",
    "just scraping by", "old money", "new money", "maxed-out credit", "rags-to-riches"
 ]

def generate_character_blurb(name, traits, custom_traits, phys, fashion, wealth, drama):
    trait_list = traits.copy()
    if "Custom..." in traits and custom_traits:
        trait_list += [ct.strip() for ct in custom_traits.split(",") if ct.strip()]
    trait_list = [t for t in trait_list if t != "Custom..."]
    g_traits = ", ".join(trait_list) if trait_list else "unpredictable"
    return (
        f"**{name}**: {phys}, usually seen in {fashion}. "
        f"{name.split()[0]} is {wealth}, drama level {drama}, and has a vibe that's {g_traits.lower()}."
    )
def theme_grid(session_state, enable_new_show, key_prefix=""):
    if not enable_new_show:
        return

    st.markdown("### 1. Pick Genres & Styles")
    genres = st.multiselect(
        "Pick Genres",
        [f"{GENRE_EMOJIS[g]} {g}" for g in THEMES.keys()],
        key=f"{key_prefix}genre_multiselect"
    )
    def strip_emoji(label): return label.split(" ", 1)[1] if " " in label else label
    genres_clean = [strip_emoji(g) for g in genres]
    chosen_styles = []
    for genre in genres_clean:
            emoji = GENRE_EMOJIS.get(genre, "")
            st.markdown(f"#### {emoji} {genre}")
            shows = THEMES[genre]
            cols = st.columns(len(shows))
            for idx, show in enumerate(shows):
                spicy_keywords = [
                    "spicy", "drama", "raunchy", "affair", "betrayal",
                    "freaky", "nude", "sex", "kink", "strip", "cringe",
                    "makeout", "tantric", "orgy", "lusty", "bikini"
                ]
                spicy = any(word in show["desc"].lower() for word in spicy_keywords)
                pepper = "🌶️" if spicy else ""
                bg_style = "background-color:#ffe5e5;" if spicy else ""
                with cols[idx]:
                    st.markdown(
                        f"<div style='border-radius:10px; padding:12px; {bg_style}'>"
                        f"<b>{show['name']} {pepper}</b><br><span style='font-size:90%;'>{show['desc']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    c = st.checkbox(
                        f"Select {show['name']}",
                        key=f"showstyle_{genre}_{show['name']}"
                    )
                    if c:
                        chosen_styles.append(show['name'])
    if chosen_styles:
        if st.button("Continue to Character Builder", key=f"{key_prefix}to_chars"):
            session_state["genre_done"] = True
            session_state["theme"] = genres
            session_state["style"] = chosen_styles

    if session_state.get("genre_done"):
        st.markdown("---")
        st.markdown("### 2. Character Builder")
        if f"{key_prefix}cast_names_input" not in session_state:
            session_state[f"{key_prefix}cast_names_input"] = "Alex, Jamie, Taylor"
        cast_names_input = st.text_area(
            "Cast Names (comma separated)",
            session_state[f"{key_prefix}cast_names_input"],
            key=f"{key_prefix}cast_names_area"
        )
        cast = [c.strip() for c in cast_names_input.split(",") if c.strip()]
        session_state[f"{key_prefix}cast_names_input"] = cast_names_input

        has_host = st.checkbox("Include a Host Character", key=f"{key_prefix}has_host")
        host_name = ""
        if has_host:
            host_name = st.text_input("Host Name", value="Maury", key=f"{key_prefix}host_name")

        char_list = cast.copy()
        if has_host and host_name:
            char_list.append(host_name)

        # Per-character builder state
        def state_get(attr, default):
            return session_state.get(f"{key_prefix}{attr}", default)
        def state_set(attr, value):
            session_state[f"{key_prefix}{attr}"] = value

        for attr, default in [
            ("char_behaviors", {}),
            ("char_custom_traits", {}),
            ("char_phys", {}),
            ("char_fashion", {}),
            ("char_wealth", {}),
            ("char_drama", {}),
        ]:
            if f"{key_prefix}{attr}" not in session_state:
                state_set(attr, default)

        char_cols = st.columns(min(3, max(1, len(char_list))))
        for idx, char in enumerate(char_list):
            col = char_cols[idx % len(char_cols)]
            with col:
                st.markdown(f"**{char}**")
                char_drama = st.slider(
                    f"{char} Drama", 1, 10,
                    state_get("char_drama", {}).get(char, 5),
                    key=f"{key_prefix}drama_{char}"
                )
                session_state[f"{key_prefix}char_drama"][char] = char_drama

                traits = st.multiselect(
                    f"{char} Traits", CHARACTER_BEHAVIOR_TRAITS,
                    default=state_get("char_behaviors", {}).get(char, []),
                    key=f"{key_prefix}traits_{char}"
                )
                session_state[f"{key_prefix}char_behaviors"][char] = traits

                custom_traits = ""
                if "Custom..." in traits:
                    custom_traits = st.text_input(
                        f"{char} Custom traits",
                        state_get("char_custom_traits", {}).get(char, ""),
                        key=f"{key_prefix}custom_{char}"
                    )
                    session_state[f"{key_prefix}char_custom_traits"][char] = custom_traits

                phys = st.selectbox(
                    f"{char} Physical", PHYS_DESCS,
                    index=PHYS_DESCS.index(state_get("char_phys", {}).get(char, PHYS_DESCS[0]))
                    if state_get("char_phys", {}).get(char) in PHYS_DESCS else 0,
                    key=f"{key_prefix}phys_{char}"
                )
                session_state[f"{key_prefix}char_phys"][char] = phys

                fashion = st.selectbox(
                    f"{char} Fashion", FASHIONS,
                    index=FASHIONS.index(state_get("char_fashion", {}).get(char, FASHIONS[0]))
                    if state_get("char_fashion", {}).get(char) in FASHIONS else 0,
                    key=f"{key_prefix}fashion_{char}"
                )
                session_state[f"{key_prefix}char_fashion"][char] = fashion

                wealth = st.selectbox(
                    f"{char} Wealth", WEALTH,
                    index=WEALTH.index(state_get("char_wealth", {}).get(char, WEALTH[0]))
                    if state_get("char_wealth", {}).get(char) in WEALTH else 0,
                    key=f"{key_prefix}wealth_{char}"
                )
                session_state[f"{key_prefix}char_wealth"][char] = wealth

                st.caption(generate_character_blurb(
                    char, traits,
                    session_state[f"{key_prefix}char_custom_traits"].get(char, ""),
                    phys, fashion, wealth, char_drama
                ))

        # Add a random character
        if st.button("Add Random Character", key=f"{key_prefix}rand_char_btn"):
            new_name = random.choice([n for n in RANDOM_NAMES if n not in cast])
            session_state[f"{key_prefix}cast_names_input"] += ", " + new_name
            st.experimental_rerun()

        if st.button("Continue to Show Details", key=f"{key_prefix}to_show_details"):
            session_state["chars_done"] = True

    if session_state.get("chars_done"):
        st.markdown("---")
        st.markdown("### 3. Show Details & Save")
        show_name = st.text_input("Show Name", value=session_state.get("show_name", ""), key=f"{key_prefix}show_name_main")
        overall_drama = st.slider("Overall Drama Level", 1, 10, 5, key=f"{key_prefix}overall_drama")
        session_state["show_name"] = show_name

        cast = [c.strip() for c in session_state.get(f"{key_prefix}cast_names_input", "").split(",") if c.strip()]
        if session_state.get(f"{key_prefix}has_host") and session_state.get(f"{key_prefix}host_name"):
            cast.append(session_state[f"{key_prefix}host_name"])
        show_id = show_name.strip().replace(" ", "_")
        show_obj = {
            "name": show_name,
            "theme": session_state.get("theme", []),
            "style": session_state.get("style", []),
            "drama": overall_drama,
            "cast": cast,
            "behaviors": {c: session_state[f"{key_prefix}char_behaviors"].get(c, []) for c in cast},
            "custom_traits": {c: session_state[f"{key_prefix}char_custom_traits"].get(c, "") for c in cast},
            "phys": {c: session_state[f"{key_prefix}char_phys"].get(c, "") for c in cast},
            "fashion": {c: session_state[f"{key_prefix}char_fashion"].get(c, "") for c in cast},
            "wealth": {c: session_state[f"{key_prefix}char_wealth"].get(c, "") for c in cast},
            "char_drama": {c: session_state[f"{key_prefix}char_drama"].get(c, 5) for c in cast},
            "has_host": session_state.get(f"{key_prefix}has_host", False),
            "host_name": session_state.get(f"{key_prefix}host_name", "") if session_state.get(f"{key_prefix}has_host") else "",
            "seasons": {}
        }
        if st.button("Save Show", key=f"{key_prefix}save_show_btn"):
            show_dir = os.path.join("data", "shows", show_id)
            os.makedirs(show_dir, exist_ok=True)
            meta_path = os.path.join(show_dir, "metadata.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(show_obj, f, indent=2)
            # --- Fix: Also create corresponding media video dir ---
            video_dir = os.path.join("data", "media", "show_videos", show_id)
            os.makedirs(video_dir, exist_ok=True)
            st.success(f"Show '{show_name}' created and saved!")

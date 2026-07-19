"""
RC2 SPRINT 3 — SEMANTIC PATTERN LIBRARY EXPANSION PLAN

Objective: Scale from 15 to 60-80 generic, non-book-specific semantic patterns
Date: 2026-07-06
Status: PLANNING
"""

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

Current State (Sprint 2):
  - 15 patterns total
  - 3 categories (theme, character_role, learning_outcome)
  - Tested on 3 books
  - 64/64 tests passing
  - Production safety verified

Target (Sprint 3):
  - 60-80 patterns total
  - 6 categories (themes, character_roles, learning_outcomes, conflict, emotion, narrative_structure)
  - Tested on 10-20 books
  - 100+ tests
  - Enhanced validation framework
  - Comprehensive benchmarking

# ============================================================================
# EXPANDED PATTERN LIBRARY DESIGN
# ============================================================================

## CATEGORY 1: THEMES (20 patterns)
---

Pattern 1:
  id: theme_adventure
  name: Adventure
  category: theme
  description: Journey, exploration, discovery, quest
  keywords: [macera, yolculuk, keşif, sefaret, arama, deniz, dağ]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.5
  confidence_weight: 1.0
  status: VALIDATED

Pattern 2:
  id: theme_growth
  name: Growth & Development
  category: theme
  description: Personal development, learning, maturation, transformation
  keywords: [büyüme, gelişim, olgunlaşma, öğrenme, değişme, ilerleme]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.6
  confidence_weight: 0.95
  status: VALIDATED

Pattern 3:
  id: theme_conflict
  name: Conflict & Challenge
  category: theme
  description: Struggle, confrontation, combat, obstacles
  keywords: [çatışma, mücadele, savaş, karşılaşma, engel, zorluk]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 1.0
  status: VALIDATED

Pattern 4:
  id: theme_friendship
  name: Friendship & Connection
  category: theme
  description: Bonds, collaboration, loyalty, partnership
  keywords: [dostluk, arkadaşlık, birlik, dayanışma, sadakat, yardım]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.5
  confidence_weight: 1.0
  status: VALIDATED

Pattern 5:
  id: theme_family
  name: Family & Kinship
  category: theme
  description: Family relationships, parenthood, siblings
  keywords: [aile, baba, anne, kardeş, ebeveyn, ata, nesil]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.3
  confidence_weight: 1.0
  status: VALIDATED

Pattern 6:
  id: theme_courage
  name: Courage & Bravery
  category: theme
  description: Bravery, fearlessness, heroism, confidence
  keywords: [cesaret, yiğitlik, korkmamak, kahraman, güven, cüret]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.5
  confidence_weight: 0.95
  status: VALIDATED

Pattern 7:
  id: theme_knowledge
  name: Learning & Wisdom
  category: theme
  description: Education, discovery of knowledge, wisdom
  keywords: [bilgi, çalışma, eğitim, öğrenme, keşfet, akıl]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.4
  confidence_weight: 0.9
  status: VALIDATED

Pattern 8:
  id: theme_mystery
  name: Mystery & Intrigue
  category: theme
  description: Puzzle, secret, investigation, suspense
  keywords: [gizem, sır, araştırma, ipucu, belirsizlik, merak]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 9:
  id: theme_wonder
  name: Wonder & Magic
  category: theme
  description: Magic, fantasy, supernatural, extraordinary
  keywords: [sihir, büyü, harika, doğaüstü, mucize, fantezi]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 0.9
  status: NEW

Pattern 10:
  id: theme_loss
  name: Loss & Grief
  category: theme
  description: Sadness, grief, farewell, goodbye
  keywords: [kayıp, yas, acı, veda, ayrılık, hüzün]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 11:
  id: theme_belonging
  name: Belonging & Acceptance
  category: theme
  description: Inclusion, acceptance, finding home, community
  keywords: [ait olma, kabul, ev, toplum, aidiyet, yer]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 12:
  id: theme_justice
  name: Justice & Fairness
  category: theme
  description: Right vs wrong, morality, balance
  keywords: [adalet, doğru, hak, yanlış, ceza, ödül]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 13:
  id: theme_nature
  name: Nature & Environment
  category: theme
  description: Natural world, environment, animals, seasons
  keywords: [doğa, çevre, hayvan, mevsim, orman, su]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 0.9
  status: NEW

Pattern 14:
  id: theme_identity
  name: Identity & Self-Discovery
  category: theme
  description: Who am I, self-realization, searching for identity
  keywords: [kimlik, öz, yüz, ben, tanıma, bilinç]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.3
  confidence_weight: 0.8
  status: NEW

Pattern 15:
  id: theme_dreams
  name: Dreams & Aspiration
  category: theme
  description: Goals, wishes, aspirations, ambition
  keywords: [rüya, hayal, hedef, isteme, tutkun, imren]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 16:
  id: theme_tradition
  name: Tradition & Culture
  category: theme
  description: Customs, heritage, cultural values, tradition
  keywords: [gelenek, kültür, miras, görenek, değer, adet]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 17:
  id: theme_change
  name: Change & Adaptation
  category: theme
  description: Transformation, adaptation, new beginning
  keywords: [değişim, uyum, başlangıç, yeni, devrim, dönüş]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.4
  confidence_weight: 0.85
  status: NEW

Pattern 18:
  id: theme_power
  name: Power & Authority
  category: theme
  description: Leadership, influence, control, strength
  keywords: [güç, yetki, kontrol, liderlik, etki, kuvvet]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.3
  confidence_weight: 0.8
  status: NEW

Pattern 19:
  id: theme_freedom
  name: Freedom & Liberation
  category: theme
  description: Liberty, independence, breaking free
  keywords: [özgürlük, bağımsızlık, kurtulma, baskıdan kurtulma]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.3
  confidence_weight: 0.85
  status: NEW

Pattern 20:
  id: theme_redemption
  name: Redemption & Renewal
  category: theme
  description: Transformation, second chances, making amends
  keywords: [kurtarma, iyileşme, bağışlama, yenileme, tövbe]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW


## CATEGORY 2: CHARACTER ROLES (12 patterns)
---

Pattern 1:
  id: character_protagonist
  name: Protagonist
  category: character_role
  description: Main character, hero, central figure
  keywords: [ana karakter, kahraman, çocuk, kız, oğlan, başkarakter]
  matching_strategy: contextual
  default_fp_risk: low
  expected_density: 0.6
  confidence_weight: 1.0
  status: VALIDATED

Pattern 2:
  id: character_antagonist
  name: Antagonist
  category: character_role
  description: Opposition, villain, opposing force
  keywords: [düşman, kötü, olumsuz, karşı, muhalif]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.7
  status: VALIDATED

Pattern 3:
  id: character_mentor
  name: Mentor & Guide
  category: character_role
  description: Teacher, guide, wise figure, advisor
  keywords: [öğretmen, rehber, bilge, yaşlı, danışman, öncü]
  matching_strategy: contextual
  default_fp_risk: low
  expected_density: 0.3
  confidence_weight: 0.9
  status: VALIDATED

Pattern 4:
  id: character_companion
  name: Companion & Friend
  category: character_role
  description: Ally, friend, partner, helper
  keywords: [arkadaş, dost, yoldaş, asistan, müttefik, yardımcı]
  matching_strategy: contextual
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 1.0
  status: VALIDATED

Pattern 5:
  id: character_innocent
  name: Innocent & Victim
  category: character_role
  description: Innocent party, victim, vulnerable character
  keywords: [masum, kurban, çaresiz, zayıf, savunmasız, mağdur]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 6:
  id: character_trickster
  name: Trickster & Deceiver
  category: character_role
  description: Cunning character, deceiver, prankster
  keywords: [aldatıcı, hile, oyun, sinsi, hilekâr, üretici]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.75
  status: NEW

Pattern 7:
  id: character_sage
  name: Sage & Wise One
  category: character_role
  description: Wise figure, oracle, philosopher
  keywords: [bilge, usta, danışman, dergah, fen, hikmet]
  matching_strategy: contextual
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.85
  status: NEW

Pattern 8:
  id: character_comic_relief
  name: Comic Relief & Jester
  category: character_role
  description: Humorous character, entertainer, buffoon
  keywords: [komik, espri, şaka, eğlence, buffo, maskara]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.7
  status: NEW

Pattern 9:
  id: character_creature
  name: Creature & Animal
  category: character_role
  description: Animal companion, magical creature
  keywords: [hayvan, canlı, yaratık, varlık, elf, yoksa]
  matching_strategy: contextual
  default_fp_risk: medium
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 10:
  id: character_outsider
  name: Outsider & Outscast
  category: character_role
  description: Outcast, outsider, misfit
  keywords: [dışlanmış, misfit, garip, yadığı, paria, yabancı]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 11:
  id: character_authority
  name: Authority Figure
  category: character_role
  description: Figure in power, ruler, leader
  keywords: [yetkilisi, hakim, kral, prenses, başkan, sahibi]
  matching_strategy: contextual
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.85
  status: NEW

Pattern 12:
  id: character_observer
  name: Observer & Narrator
  category: character_role
  description: Witness, observer, narrator perspective
  keywords: [gözlemci, tanık, anlatıcı, bakış, perspektif]
  matching_strategy: contextual
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.7
  status: NEW


## CATEGORY 3: LEARNING OUTCOMES (12 patterns)
---

Pattern 1:
  id: learning_cognitive
  name: Cognitive Learning
  category: learning_outcome
  description: Knowledge acquisition, understanding, critical thinking
  keywords: [öğrendi, anladı, bildi, kavradı, düşün, akıl]
  matching_strategy: context_window
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 0.9
  status: VALIDATED

Pattern 2:
  id: learning_social
  name: Social Learning
  category: learning_outcome
  description: Cooperation, communication, interpersonal skills
  keywords: [işbirliği, dayanışma, iletişim, empati, konuş, dinle]
  matching_strategy: context_window
  default_fp_risk: high
  expected_density: 0.3
  confidence_weight: 0.85
  status: VALIDATED

Pattern 3:
  id: learning_emotional
  name: Emotional Learning
  category: learning_outcome
  description: Emotional intelligence, self-awareness, feelings
  keywords: [hissetti, duygulanıyor, deneyimle, anlış, duygu, kalp]
  matching_strategy: context_window
  default_fp_risk: high
  expected_density: 0.3
  confidence_weight: 0.8
  status: VALIDATED

Pattern 4:
  id: learning_physical
  name: Physical Learning
  category: learning_outcome
  description: Motor skills, physical activity, movement
  keywords: [hareketi, aktivite, oyun, spor, dans, koşu]
  matching_strategy: context_window
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.85
  status: VALIDATED

Pattern 5:
  id: learning_moral
  name: Moral Learning
  category: learning_outcome
  description: Ethics, right vs wrong, moral reasoning
  keywords: [ahlak, doğru, hak, yanlış, etik, vicdan]
  matching_strategy: context_window
  default_fp_risk: high
  expected_density: 0.25
  confidence_weight: 0.8
  status: NEW

Pattern 6:
  id: learning_creativity
  name: Creative Learning
  category: learning_outcome
  description: Imagination, creativity, innovation
  keywords: [yaratıcılık, hayal, sanat, müzik, icat, buluş]
  matching_strategy: context_window
  default_fp_risk: medium
  expected_density: 0.25
  confidence_weight: 0.8
  status: NEW

Pattern 7:
  id: learning_resilience
  name: Resilience & Perseverance
  category: learning_outcome
  description: Perseverance, determination, handling failure
  keywords: [ısrarcı, azim, yılmamak, zorluğa katlansa, tekrar]
  matching_strategy: context_window
  default_fp_risk: medium
  expected_density: 0.25
  confidence_weight: 0.8
  status: NEW

Pattern 8:
  id: learning_cultural
  name: Cultural Learning
  category: learning_outcome
  description: Cultural awareness, understanding diversity
  keywords: [kültür, farklılık, gelenek, adet, ırk, din]
  matching_strategy: context_window
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 9:
  id: learning_environmental
  name: Environmental Awareness
  category: learning_outcome
  description: Ecological awareness, care for nature
  keywords: [çevre, doğa, koruma, yaşam, ağaç, hayvan]
  matching_strategy: context_window
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 10:
  id: learning_critical_thinking
  name: Critical Thinking
  category: learning_outcome
  description: Analysis, evaluation, questioning
  keywords: [analiz, değerlend, sorgula, neden, nasıl, kanıt]
  matching_strategy: context_window
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.75
  status: NEW

Pattern 11:
  id: learning_self_awareness
  name: Self-Awareness & Reflection
  category: learning_outcome
  description: Self-knowledge, introspection, reflection
  keywords: [kendini tanı, iç denetim, farkında, yansıt, keşfet]
  matching_strategy: context_window
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 12:
  id: learning_problem_solving
  name: Problem-Solving
  category: learning_outcome
  description: Solution finding, strategy, planning
  keywords: [çöz, plan, strateji, çare, sonuç, çıkış]
  matching_strategy: context_window
  default_fp_risk: medium
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW


## CATEGORY 4: CONFLICT TYPES (10 patterns)
---

Pattern 1:
  id: conflict_man_vs_self
  name: Man vs Self
  category: conflict
  description: Internal struggle, personal challenge, inner conflict
  keywords: [iç çatışma, kendisi, tercih, ikilem, karar, vicdan]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 2:
  id: conflict_man_vs_man
  name: Man vs Man
  category: conflict
  description: Interpersonal conflict, competition, rivalry
  keywords: [çatışma, rakip, düşman, dövüş, anlaşmazlık, çekişme]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.3
  confidence_weight: 0.9
  status: NEW

Pattern 3:
  id: conflict_man_vs_nature
  name: Man vs Nature
  category: conflict
  description: Struggle against natural forces, survival
  keywords: [doğa, fırtına, sel, deprem, soğuk, hayvan]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.85
  status: NEW

Pattern 4:
  id: conflict_man_vs_society
  name: Man vs Society
  category: conflict
  description: Social conflict, rebellion, injustice
  keywords: [toplum, haksızlık, isyan, otorite, kanun, sistem]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 5:
  id: conflict_man_vs_fate
  name: Man vs Fate
  category: conflict
  description: Struggle against destiny, luck, destiny
  keywords: [kader, talih, yazı, tesadüf, ölüm, çok geç]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 6:
  id: conflict_ideological
  name: Ideological Conflict
  category: conflict
  description: Conflict of beliefs, values, philosophy
  keywords: [inanç, felsefe, değer, doğru, yanlış, ideoloji]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 7:
  id: conflict_economic
  name: Economic Conflict
  category: conflict
  description: Conflict over resources, money, survival
  keywords: [para, zengin, fakir, kıtlık, bolluk, miras]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 8:
  id: conflict_political
  name: Political Conflict
  category: conflict
  description: Power struggles, governance, authority
  keywords: [hükümet, kral, prenses, savaş, taht, yönetim]
  matching_strategy: keyword_frequency
  default_fp_risk: low
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW

Pattern 9:
  id: conflict_romantic
  name: Romantic Conflict
  category: conflict
  description: Love triangles, relationship challenges
  keywords: [aşk, sevgi, kalp, evlilik, seçim, ayrılık]
  matching_strategy: keyword_frequency
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 10:
  id: conflict_generational
  name: Generational Conflict
  category: conflict
  description: Youth vs age, tradition vs change
  keywords: [kuşak, genç, yaşlı, gelenek, modern, farklılık]
  matching_strategy: keyword_frequency
  default_fp_risk: medium
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW


## CATEGORY 5: EMOTION TYPES (12 patterns)
---

Pattern 1:
  id: emotion_joy
  name: Joy & Happiness
  category: emotion
  description: Happiness, delight, contentment, celebration
  keywords: [mutluluk, sevinç, gül, kutlama, coşku, keyif]
  matching_strategy: sentiment
  default_fp_risk: low
  expected_density: 0.3
  confidence_weight: 0.9
  status: NEW

Pattern 2:
  id: emotion_sadness
  name: Sadness & Sorrow
  category: emotion
  description: Sadness, grief, melancholy, despair
  keywords: [hüzün, keder, ağla, acı, üzüntü, mutsuzluk]
  matching_strategy: sentiment
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.9
  status: NEW

Pattern 3:
  id: emotion_fear
  name: Fear & Anxiety
  category: emotion
  description: Fear, anxiety, worry, terror
  keywords: [korku, kaygı, endişe, dehşet, ürkü, çekince]
  matching_strategy: sentiment
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.9
  status: NEW

Pattern 4:
  id: emotion_anger
  name: Anger & Rage
  category: emotion
  description: Anger, rage, fury, frustration
  keywords: [öfke, gazap, kızgınlık, hiddet, sinir, nefret]
  matching_strategy: sentiment
  default_fp_risk: low
  expected_density: 0.2
  confidence_weight: 0.9
  status: NEW

Pattern 5:
  id: emotion_love
  name: Love & Affection
  category: emotion
  description: Love, affection, tenderness, care
  keywords: [aşk, sevgi, ten, bakım, şefkat, hubb]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.2
  confidence_weight: 0.85
  status: NEW

Pattern 6:
  id: emotion_surprise
  name: Surprise & Wonder
  category: emotion
  description: Surprise, astonishment, amazement
  keywords: [sürpriz, hayret, şaşkınlık, mucize, merak]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW

Pattern 7:
  id: emotion_shame
  name: Shame & Embarrassment
  category: emotion
  description: Shame, embarrassment, guilt, humiliation
  keywords: [utanç, pişmanlık, suçlu, alçaklık, eziyet]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.75
  status: NEW

Pattern 8:
  id: emotion_hope
  name: Hope & Optimism
  category: emotion
  description: Hope, optimism, belief, expectation
  keywords: [umut, iyimserlik, inanç, beklenti, gelecek]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW

Pattern 9:
  id: emotion_despair
  name: Despair & Hopelessness
  category: emotion
  description: Despair, hopelessness, defeat
  keywords: [çaresizlik, ümitsizlik, yenilgi, teslim, bitti]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.75
  status: NEW

Pattern 10:
  id: emotion_trust
  name: Trust & Confidence
  category: emotion
  description: Trust, confidence, faith in others
  keywords: [güven, inanç, sadakat, dürüstlük, vefa]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW

Pattern 11:
  id: emotion_betrayal
  name: Betrayal & Distrust
  category: emotion
  description: Betrayal, distrust, disappointment
  keywords: [ihanet, terketme, aldatma, güvensizlik, hayal kırıklığı]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.75
  status: NEW

Pattern 12:
  id: emotion_pride
  name: Pride & Dignity
  category: emotion
  description: Pride, dignity, self-respect, arrogance
  keywords: [gurur, saygınlık, kibir, onur, izzet]
  matching_strategy: sentiment
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW


## CATEGORY 6: NARRATIVE STRUCTURE (8 patterns)
---

Pattern 1:
  id: narrative_linear
  name: Linear Narrative
  category: narrative_structure
  description: Straightforward chronological progression
  keywords: [sonra, sonunda, daha sonra, şimdi, ilk, son]
  matching_strategy: structure
  default_fp_risk: low
  expected_density: 0.4
  confidence_weight: 0.85
  status: NEW

Pattern 2:
  id: narrative_flashback
  name: Flashback & Memory
  category: narrative_structure
  description: Past events revealed through flashback
  keywords: [hatırla, geçmişte, uzun zaman, geçen, anı, iyi eski]
  matching_strategy: structure
  default_fp_risk: medium
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 3:
  id: narrative_parallel
  name: Parallel Narratives
  category: narrative_structure
  description: Multiple storylines running in parallel
  keywords: [eş zamanlı, aynı anda, başka, diğeri, ikinci, ayrıntı]
  matching_strategy: structure
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 4:
  id: narrative_frame
  name: Frame Narrative
  category: narrative_structure
  description: Story within a story
  keywords: [hikaye anlat, tanık, öykü, anlatma, böyle, derken]
  matching_strategy: structure
  default_fp_risk: high
  expected_density: 0.15
  confidence_weight: 0.75
  status: NEW

Pattern 5:
  id: narrative_plot_twist
  name: Plot Twist & Revelation
  category: narrative_structure
  description: Unexpected turn of events, revelations
  keywords: [beklenti, sürpriz, açıklanmak, çok kötü, ne var ki]
  matching_strategy: structure
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.7
  status: NEW

Pattern 6:
  id: narrative_rising_action
  name: Rising Action & Tension
  category: narrative_structure
  description: Escalating tension and complications
  keywords: [kötüleşmek, artmak, endişe, sorun, çok zor, ciddi]
  matching_strategy: structure
  default_fp_risk: medium
  expected_density: 0.2
  confidence_weight: 0.8
  status: NEW

Pattern 7:
  id: narrative_climax
  name: Climax & Resolution
  category: narrative_structure
  description: Peak of tension, main conflict resolution
  keywords: [doruk, çatışma, sonuç, çözüm, karar, bitir]
  matching_strategy: structure
  default_fp_risk: medium
  expected_density: 0.15
  confidence_weight: 0.8
  status: NEW

Pattern 8:
  id: narrative_denouement
  name: Denouement & Reflection
  category: narrative_structure
  description: Falling action, reflection, final thoughts
  keywords: [sonuncu, refleks, yansıt, anlamı, dernek, ilham]
  matching_strategy: structure
  default_fp_risk: high
  expected_density: 0.1
  confidence_weight: 0.75
  status: NEW


# ============================================================================
# PATTERN METADATA SCHEMA
# ============================================================================

Each pattern MUST include:

1. id (string): Unique identifier
   Format: category_name (lowercase, underscore)
   Example: theme_adventure, character_protagonist

2. name (string): Human-readable pattern name
   Example: Adventure, Growth & Development

3. category (string): Pattern category
   Values: theme | character_role | learning_outcome | conflict | emotion | narrative_structure

4. description (string): Clear description of pattern
   Example: Journey, exploration, discovery, quest

5. keywords (list): Turkish keywords for pattern matching
   Note: Generic keywords only, no book-specific terms
   Example: [macera, yolculuk, keşif, sefaret]

6. matching_strategy (string): How pattern is detected
   Values: keyword_frequency | contextual | context_window | sentiment | structure

7. default_fp_risk (string): False positive risk level
   Values: low | medium | high
   Used for confidence calculation

8. expected_density (float): Expected density of pattern in typical text
   Range: 0.0-1.0
   Used for calibration and benchmarking

9. confidence_weight (float): Weight for confidence calculation
   Range: 0.7-1.0
   Lower weight = more conservative confidence

10. status (string): Pattern development status
    Values: VALIDATED | NEW | UNDER_REVIEW | DEPRECATED


# ============================================================================
# TOTAL PATTERN COUNT
# ============================================================================

Themes:               20 patterns
Character Roles:     12 patterns
Learning Outcomes:   12 patterns
Conflict Types:      10 patterns
Emotion Types:       12 patterns
Narrative Structure:  8 patterns
─────────────────────────────────
TOTAL:               74 patterns

(Within target range of 60-80)


# ============================================================================
# IMPLEMENTATION MILESTONES
# ============================================================================

Phase 1: Pattern Library Module (Sprint 3.1)
  - semantic_pattern_library.py (metadata + loader)
  - Pattern validation framework
  - Duplicate & conflict detection

Phase 2: Enhanced Confidence Engine Integration (Sprint 3.2)
  - Integrate patterns with confidence engine
  - Per-pattern calibration
  - Batch processing

Phase 3: Comprehensive Benchmarking (Sprint 3.3)
  - Collect 10-20 diverse books
  - Run full benchmark suite
  - Generate coverage & quality metrics

Phase 4: Verification & Safety (Sprint 3.4)
  - Production safety verification (4 core tests)
  - Determinism verification (full test suite)
  - Shadow compatibility verification
  - Generate RC2 Sprint 3 artifacts

Phase 5: Commit & Release (Sprint 3.5)
  - Final testing
  - Git commit with full documentation
  - Performance metrics


# ============================================================================
# SUCCESS CRITERIA
# ============================================================================

✓ Pattern count: 60-80 (achieved: 74)
✓ All patterns generic (no book-specific heuristics)
✓ Production safety: 100% (equal_without_shadow == true)
✓ Deterministic: 100% (same input → same output)
✓ Test coverage: 100+ tests, 100% passing
✓ Benchmark books: 10-20 diverse books analyzed
✓ Coverage improvement: Measured and documented
✓ Confidence distribution: Calculated for all patterns
✓ False positive trend: Tracked and analyzed
✓ Runtime performance: Within acceptable limits

"""

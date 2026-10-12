
# -------------------------------------------------- 名詞／形容詞／副詞詞庫
NOUN_SET = set("""
address advertisement advice afternoon album ambulance apartment app armchairs
article assistant aunt bag bags bank basket basketball bathroom beach bed
bedrooms beginning bill bin birds board book books boss bottle bottles bowl box
boxes breakfast bridge brother bus cafe cake camera campsite card centre chat
child childhood cinema city class classmate classmates classroom clock cloth
clothes clouds club coach coast coat coffee colours computer cooker corner
costumes country course cousin cream cup cups curtains customer danger date
daughter day days difference dining dinner door draft drama driver egg
electricity effort end ending exam example eyes fact facts family farm farmer
father festival fever fields file floor floors flour food foot forest forks
form front fruit game games gas gate gift girl glasses grandfather grandmother
grandparents group groups guest gym hall handbag hands handwriting headache
heating hobby home homework hospital hotel hour hours house idea information
ingredients island item jacket jeans job journey juice keyboard kind kinds
kitchen knife label lake lamp lesson lessons library list litre locker lunch
machine magazine manager map market maths member members message milk
millilitres minutes mirror mistake mistakes moment money monitor month months
mountain mountains mouse museum music name names necklace news newspaper night
noise noodles noon note notebook notebooks notes number nurse ocean office
opinion oven page pain paper parents part partner password path patients
patterns people petrol photo photograph photographs photography photos picnic
pictures pilot place plate platform player players pocket points police pool post
postcards pounds practice presentation price prize problem progress project quiz
race railway rain raincoat repairman report responsibility result river rivers
room rubbish rule ruler rules sale sandwich sandwiches scale scarf scene school
science scientist screen sea sentence sentences shape shelves shift shirt
sister size skirt sky sofa software source speech stairs staircase staff stomach
storm story street subject summer sun supermarket table taxi teacher team
teenager temperature tent tents term test text textbook throat time times tool
tools top town traffic train trainers training trip trophy trousers unit
university uniform village voice voices volunteer wall walls water way web
website week weekend weekends weeks weight window windows winter winner winners
word words work worker year years yuan stomachache
""".split())
NOUN_PLURAL = set(w for w in NOUN_SET if w.endswith('s'))

ADJ_SET = set("""
afraid angry asleep bare big black blue bored boring brave bright brilliant
busy careful cheap clear cloudy cold comfortable cool dangerous dark delicious
different dirty easy expensive excited exciting fine fresh friendly full funny
glad golden good great green grey happy heavy high hot hungry important
interesting ill kind large late local long loud lovely lucky main meaningful
narrow nervous new nice noisy old pale pink polite poor pretty proud quiet
ready rich rude sad safe same scared short shy simple small soft sore special
strange strong successful sure sweet tall terrible thin tight tired true ugly
uncomfortable unhappy unkind useful warm white wide windy wonderful wrong
young youngest yellow extra flat round sunny cloudy empty tasty tidy
""".split())

ADV_SET = set("""
actually again almost alone aloud already also always away badly carefully
completely exactly extremely far heavily here however loudly never now often
politely quite rather really slowly sometimes soon still straight suddenly
together twice upstairs usually very instead then even further earlier sooner
later together elsewhere ago ago indeed certainly probably perhaps obviously
clearly simply merely ever meanwhile therefore hence otherwise besides
""".split())

# 比較級／最高級：形容詞或副詞兩可
COMPARATIVE = set("""faster easier harder higher smaller slower lighter
stronger faster quicker nearer cheaper wider shorter longer darker clearer
sooner further better best worse worst least closer deeper quicker fatter
""".split())

# ---- 補充詞庫（逐字檢視後補入） ----
NOUN_SET |= set("""age comma competition dentist desk diary dictionary doctor
exercise fridge friend future hat ice internet key letter lot medicine mother
neighbour pair question recipe restaurant road schedule shop song station
stationery student sugar survey television tourist tree uncle weather wood
cartoon cabbage shelf corner chance memory journey garden letter""".split())
NOUN_PLURAL |= set(w for w in NOUN_SET if w.endswith('s'))

ADJ_SET |= set("""calm direct favourite final mobile real sorry single weak wet
wooden likely silver comfortable delicious delicious""".split())

ADV_SET |= set("""proudly quietly too furthermore moreover"""
                .split())

INTJ_SET = set("""yes please oh wow hello hi goodbye thanks cheers""".split())

PREP_BEHIND = set("""behind below beyond opposite toward via""".split())
COMPARATIVE |= set("""braver brighter cleaner clearest easier faster happiest
harder higher lighter slower smaller stronger taller thicker worse""".split())

# ---- 第二批補入 ----
NOUN_SET |= set('sundays'.split())

# 被 verb_morph 誤判成動名詞的純名詞（building a tall building …）
NOUN_SET |= set("""building evening morning""".split())

# 本語料裡 email 一律是名詞（email address …），不是動詞
NOUN_SET |= set('email'.split())
NOUN_PLURAL |= set(['sundays'])

# 字尾是 s，但其實是單數或不可數的名詞（絕不可標成「複數」）
MASS_SINGULAR = set("""address boss bus class gas maths news progress
series species""".split())
NOUN_PLURAL -= MASS_SINGULAR

# 少數純形容詞未收進 ADJ_SET，卻會被 verb_morph 誤判成第三人稱單數
ADJ_SET |= set("""serious famous curious generous mysterious obvious various
previous obvious useful harmful nervous""".split())
PROPN |= set('ben'.split())

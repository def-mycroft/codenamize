# codenamize module
# Generate consistent easier-to-remember codenames from strings and numbers.
# Jose Juan Montes 2015-2016 - MIT License
import six

"""
Returns consistent codenames for objects, by joining
adjectives and words together. These are easier to remember and
write down than pure numbers, and can be used instead or along UUIDs,
GUIDs, hashes (MD5, SHA...), network addresses and other difficult
to remember strings.

This can be used to replace identifiers or codes when presenting those to users.
As words are easier to identify and remember for humans, this module maps
python objects to easy to remember words.

Usage
-----

Import the codenamize function:

    >>> from codenamize import codenamize

Consecutive numbers yield differentiable codenames:

    >>> codenamize("1")
    'familiar-grand'
    >>> codenamize("2")
    'little-tip'

If you later want to add more adjectives, your existing codenames
are retained as suffixes:

    >>> codenamize("11:22:33:44:55:66")
    'craven-delivery'
    >>> codenamize("11:22:33:44:55:66", 2)
    'separate-craven-delivery'

Integers are internally converted to strings:

    >>> codenamize(1)
    'familiar-grand'

Other options (max characters, join character, capitalize):

    >>> codenamize(0x123456aa, 2, 3, '', True)
    'SadBigFat'
    >>> codenamize(0x123456aa, 2, 0, '', True)
    'BrawnyEminentBear'
    >>> codenamize(0x123456aa, 4, 0, ' ', False)
    'disagreeable modern brawny eminent bear'


Examples
--------

For numbers 100000-100009 show codenames with 0-2 adjectives and different options:

    OBJ       ADJ0-MAX5    ADJ1-MAX5         ADJ2-MAX5  ADJ-0, ADJ-1, ADJ-2 (capitalized, empty join character)
    100001         boat   funny-boat   real-funny-boat  Community, RacialCommunity, PluckyRacialCommunity
    100002        award  first-award  tidy-first-award  Repeat, UptightRepeat, HelpfulUptightRepeat
    100003         rush   super-rush  equal-super-rush  Intention, ExpensiveIntention, JazzyExpensiveIntention
    100004        uncle   calm-uncle   icky-calm-uncle  March, SubduedMarch, AdamantSubduedMarch
    100005        salad   warm-salad   true-warm-salad  Plant, QuickestPlant, ReminiscentQuickestPlant
    100006         gift   witty-gift    odd-witty-gift  Estimate, CreepyEstimate, SpectacularCreepyEstimate
    100007          son     zany-son    gaudy-zany-son  Truck, MiniatureTruck, OptimalMiniatureTruck
    100008        angle   damp-angle  dusty-damp-angle  Steak, SpectacularSteak, RightfulSpectacularSteak
    100009         link   utter-link   null-utter-link  Bike, ImportantBike, SweetImportantBike

Codename space sizes
--------------------

In selecting the number of adjectives and max chars to use, consider how
many codenames you need to fit the number of objects you'll handle, since
the probability of collision increases with the number of different objects
used.

    0 adj (max 3 chars) = 115 combinations
    0 adj (max 4 chars) = 438 combinations
    0 adj (max 5 chars) = 742 combinations
    0 adj (max 6 chars) = 987 combinations
    0 adj (max 7 chars) = 1176 combinations
    0 adj (max 0 chars) = 1525 combinations
    1 adj (max 3 chars) = 2760 combinations
    1 adj (max 4 chars) = 56940 combinations
    1 adj (max 5 chars) = 241150 combinations
    1 adj (max 6 chars) = 492513 combinations
    1 adj (max 7 chars) = 789096 combinations
    1 adj (max 0 chars) = 1701900 combinations
    2 adj (max 3 chars) = 66240 combinations
    2 adj (max 4 chars) = 7402200 combinations
    2 adj (max 5 chars) = 78373750 combinations
    2 adj (max 6 chars) = 245763987 combinations
    2 adj (max 7 chars) = 529483416 combinations
    2 adj (max 0 chars) = 1899320400 combinations

An example is shown by running  codenamize --tests .
"""

import argparse
import hashlib
import functools
import sys


ADJECTIVES = [
    "low", "dim", "open", "soft", "vast", "calm", "deep", "slow", "pure", "worn", "easy",
    "cool", "airy", "bare", "late", "lean", "still", "empty", "quiet", "whole", "light",
    "clear", "aware", "loose", "fresh", "plain", "faint", "lowly", "woven", "mossy",
    "early", "simple", "humble", "rooted", "gentle", "subtle", "silent", "supple",
    "hidden", "serene", "tender", "folded", "modest", "honest", "sparse", "fallow",
    "dimlit", "spaced", "silted", "shaded", "veiled", "hollow", "mellow", "flowing",
    "natural", "patient", "present", "rounded", "playful", "aligned", "bending",
    "unbound", "ancient", "letting", "swaying", "distant", "willing", "lowborn",
    "moonlit", "slender", "untamed", "cracked", "resting", "soothed", "dawnlit",
    "settled", "leafing", "gentled", "unforced", "yielding", "grounded", "balanced",
    "flexible", "timeless", "dwelling", "fragrant", "tranquil", "gracious", "seasoned",
    "drifting", "watchful", "receding", "floating", "unsought", "gentlest", "seasonal",
    "spiraled", "shadowed", "pathless", "barefoot", "returning", "wandering", "weathered",
    "welcoming", "listening", "unhurried", "breathing", "receptive", "submerged",
    "limber", "resting", "soothed", "settled", "hidden", "deepest", "lightest", "emptiest",
    "earliest", "latest", "softest", "stillest", "quietest", "gentlest", "barest",
    "oldest", "simplest", "deepening", "bright", "shifting", "softening", "cooling",
    "warming", "floating", "wandering", "settling", "stilling", "spreading", "clearing"
]

ADJECTIVES.extend([
    "clearer", "lighter", "slower", "deeper", "softer", "emptier", "vaster", "cooler", "quieter", "warmer", "simpler", "purer", "looser", "steadier", "smoother", "broader", "lower", "lighter", "gentler", "older", "younger", "brighter", "dimmed", "rooting", "bending", "flowing", "glimmering", "settling", "wandering", "drifting", "stilling", "listening", "welcoming", "shifting", "dimming", "spreading", "loosening", "warming", "cooling", "opening", "closing", "stretching", "thinning", "clearing", "rising", "lowering", "folding", "gathering", "quieting", "softening", "pausing", "stilling", "waiting", "breathing", "touching", "holding", "resting", "yielding", "balancing", "spanning", "swaying", "hovering", "leaning", "lingering", "hollowing", "brimming", "spilling", "sheltering", "blooming", "fading", "returning", "renewing", "opening", "closing", "growing", "shrinking", "waning", "waxing", "stilling", "sinking", "rising", "broadening", "narrowing", "stilling", "lengthening", "shortening", "deepening", "shallowing", "anchoring", "loosening", "softening", "hardening", "filling", "emptying", "gleaming", "shadowing", "clouding", "clearing", "grounding", "lifting", "stretching", "breathing", "soothing", "mending"
])

ADJECTIVES.extend([
    "leafy", "misty", "woody", "stony", "muddy", "earthy", "windy", "frosty", "dewy", "dusty",
    "cloudy", "starry", "flowery", "rooted", "branching", "budding", "ripening", "shedding", "drooping", "curling",
    "drifting", "floating", "hovering", "pooling", "soaking", "melting", "fading", "glowing", "gleaming", "shimmering",
    "twining", "spiraling", "branching", "arching", "swaying", "reaching", "climbing", "crawling", "settling", "weathering",
    "softening", "hardening", "brightening", "darkening", "warming", "cooling", "soothing", "stilling", "quieting", "calming",
    "stretching", "spreading", "deepening", "broadening", "narrowing", "lengthening", "shortening", "loosening", "anchoring", "grounding",
    "sinking", "rising", "waxing", "waning", "draining", "filling", "balancing", "centering", "resting", "waiting",
    "blooming", "rippling", "trickling", "flowing", "pouring", "streaming", "raining", "snowing", "freezing", "thawing",
    "covering", "uncovering", "revealing", "veiling", "shadowing", "clearing", "opening", "closing", "forming", "dissolving",
    "returning", "pausing", "watching", "listening", "wandering", "roaming", "meandering", "lingering", "drifting", "spanning"
])

ADJECTIVES.extend([
    "rocky", "sandy", "brambly", "thorny", "grassy", "shadowy", "foggy", "hazy", "smoky", "icy",
    "glassy", "pebbly", "knotted", "twisted", "woven", "sinuous", "undulating", "layered", "banded", "ringed",
    "speckled", "spotted", "flecked", "pitted", "creased", "furrowed", "etched", "veined", "ridged", "weathered",
    "ancient", "primordial", "eldest", "immemorial", "eternal", "boundless", "measureless", "endless", "infinite", "limitless",
    "unfolding", "becoming", "rippling", "edging", "measuring", "mirroring", "reflected", "absorbing", "radiant", "gleaming",
    "whispering", "murmuring", "humming", "ringing", "singing", "resounding", "echoing", "calling", "inviting", "beckoning",
    "embracing", "holding", "enfolding", "surrounding", "cradling", "nurturing", "enclosing", "enveloping", "nesting", "harboring",
    "layering", "masking", "shading", "softening", "cooling", "warming", "freshening", "stilling", "clearing", "brightening",
    "opening", "parting", "receding", "unfolding", "arching", "curving", "rolling", "lapping", "lapping", "edging",
    "skimming", "gliding", "swaying", "shifting", "slipping", "flowing", "curling", "twisting", "sliding", "sloping"
])

ADJECTIVES.extend([
    "rootless", "tangled", "knotted", "fibrous", "woody", "barky", "lichened", "weatherbeaten", "fissured", "cracked",
    "splintered", "splitting", "shimmered", "matte", "muted", "dimmed", "smoothed", "polished", "tarnished", "blurred",
    "softened", "washed", "waterworn", "windworn", "sunworn", "faded", "bleached", "paled", "brushed", "dappled",
    "mottled", "shadowed", "deepset", "set", "imbued", "infused", "drenched", "soaked", "moistened", "parched",
    "crisp", "brittle", "papery", "grainy", "sandy", "gritty", "chalky", "clayey", "pebbled", "stubbled",
    "graveled", "silted", "tilled", "furrowed", "plowed", "seeded", "sprouted", "leafed", "flowered", "fruited",
    "barebranched", "barelimbed", "budding", "bloomed", "fallen", "scattered", "strewn", "littered", "layered", "blanketed",
    "mantled", "veiled", "hooded", "capped", "crowned", "canopied", "vaulted", "pillared", "terraced", "tiered",
    "winding", "meandering", "branching", "forking", "splitting", "braided", "laced", "threaded", "filigreed", "etched",
    "grooved", "furrowed", "pitted", "scored", "scratched", "marred", "scarred", "traced", "lined", "wrinkled"
])

ADJECTIVES.extend([
    "tumbled", "layering", "sheened", "singular", "ancient", "timely", "patient", "seasoning", "yielding", "pressing",
    "shimmering", "wavering", "burgeoning", "cresting", "soaring", "plunging", "suspended", "hovering", "wandering", "migrating",
    "seasonal", "evanescent", "delicate", "subdued", "drawn", "pale", "vivid", "fleeting", "vanishing", "gleamed",
    "flourished", "hidden", "revealed", "masked", "blended", "fused", "joined", "seamed", "woven", "braided",
    "rolling", "collapsing", "rising", "settled", "layered", "pooled", "spread", "arching", "trembling", "quivering",
    "drifting", "glowing", "yielded", "held", "carried", "borne", "drawn", "touched", "kissed", "brushed",
    "drenched", "dappled", "painted", "cast", "lifted", "turned", "folded", "shaded", "softened", "veiled",
    "borne", "whispered", "sounded", "carried", "suspended", "floating", "eddying", "circling", "ringing", "pealing",
    "glinting", "gleaming", "flashing", "glistening", "tinted", "smudged", "layered", "frosted", "iced", "melted",
    "flowed", "poured", "streamed", "widened", "narrowed", "cleansed", "smoothed", "sanded", "grained", "carved"
])



NOUNS = [
    "air", "arc", "bank", "beam", "bell", "bough", "breeze", "brook", "bud", "burl",
    "cairn", "calm", "canopy", "cave", "chime", "cliff", "cloud", "coil", "crag", "crest",
    "curve", "current", "dawn", "day", "dew", "drift", "drop", "dusk", "dust", "earth",
    "echo", "field", "fire", "flake", "flow", "fog", "fold", "foot", "form", "frost",
    "glade", "gleam", "grain", "grove", "gust", "haze", "hill", "hollow", "hue", "isle",
    "knot", "lake", "leaf", "light", "line", "moss", "mist", "moon", "mote", "mountain",
    "mud", "night", "noise", "path", "peak", "pebble", "petal", "plain", "pool", "pulse",
    "rain", "reed", "rest", "ridge", "rift", "ring", "rise", "rock", "root", "scale",
    "seed", "shade", "shadow", "shape", "shell", "shine", "shoot", "shore", "sky", "slip",
    "smoke", "snow", "soil", "song", "spark", "spine", "spring", "star", "stem", "step",
    "stone", "stream", "stripe", "sun", "tide", "time", "tone", "track", "trail", "tree",
    "trunk", "valley", "vein", "view", "vine", "voice", "wake", "wave", "way", "whirl",
    "whisper", "wind", "wing", "wood", "word", "wreath", "zenith"
]

NOUNS.extend([
    "ash", "bark", "beam", "birch", "blossom", "bloom", "bolt", "branch", "brim", "bur",
    "call", "cane", "cedar", "clay", "clearing", "climb", "cone", "cover", "crust", "dell",
    "dome", "echo", "ember", "fan", "fern", "fiber", "firefly", "flare", "flow", "foam",
    "fold", "fume", "furrow", "glimmer", "groove", "gust", "hollow", "horizon", "hum", "hush",
    "ivy", "lark", "layer", "limb", "lily", "loam", "loop", "mire", "murmur", "mycelium",
    "nest", "net", "niche", "nook", "oak", "omen", "overhang", "palm", "patch", "peak",
    "perch", "pine", "pitch", "plane", "pond", "print", "pulse", "quartz", "quiet", "reach",
    "reed", "rift", "rill", "ring", "rip", "rise", "rock", "root", "rush", "sap",
    "scatter", "scuff", "scrub", "shade", "shaft", "sheen", "shoot", "shrub", "silk", "silt",
    "slope", "smudge", "solstice", "spark", "speck", "spore", "spray", "sprig", "spur", "stack",
    "stone", "strand", "stream", "stump", "swirl", "thatch", "thicket", "thorn", "thread", "thrill",
    "thrush", "thrum", "thud", "thump", "tilt", "tint", "tongue", "track", "trickle", "twig",
    "vault", "veil", "verge", "vine", "vista", "wade", "warp", "wash", "way", "whirl",
    "willow", "wink", "wisp", "wither", "wreath", "yew"
])

NOUNS.extend([
    "ant", "ape", "bee", "beetle", "beet", "berry", "bison", "boar", "branch", "briar",
    "bull", "burrow", "carp", "cat", "cedar", "clover", "cockle", "conch", "crane", "creek",
    "cress", "crow", "deer", "dog", "dove", "eel", "egret", "elm", "falcon", "fern",
    "finch", "fish", "flint", "fowl", "fox", "frog", "furl", "goat", "goose", "hare",
    "hawk", "heron", "ibis", "jay", "koi", "leaflet", "lichen", "lotus", "magnet", "moth",
    "mulch", "mussel", "nettle", "newt", "nut", "oak", "ox", "owl", "peach", "pearl",
    "peril", "pine", "plum", "pond", "poppy", "quail", "quartz", "quill", "raven", "reed",
    "reptile", "robin", "rootlet", "rush", "rye", "salmon", "scale", "scar", "seal", "seedling",
    "shell", "shrub", "sleet", "snail", "snake", "sparrow", "spine", "squid", "stonecrop", "stork",
    "streamlet", "swan", "swift", "thorn", "thrush", "thunder", "tidepool", "toad", "topaz", "trail",
    "trickle", "trunk", "tusk", "vineyard", "vulture", "walnut", "wavelet", "weasel", "weed", "weft",
    "whale", "wheat", "wren", "zephyr", "amber", "arc", "ash", "balm", "basin", "beam", "bristle",
    "bur", "cairn", "cavern", "clod", "coil", "curl", "dune", "eddy", "flare", "fold",
    "fountain", "grove", "hollow", "jet", "lode", "mantle", "marsh", "niche", "pinnacle", "quartz",
    "rapids", "reef", "rootlet", "runoff", "rushes", "sapling", "shoal", "slope", "spume", "surf"
])

NOUNS.extend([
    "alder", "anemone", "ashlar", "asp", "atoll", "aura", "avalanche", "bamboo", "bank", "banyan",
    "basalt", "bay", "beacon", "beam", "birch", "bloom", "bluff", "bog", "boulder", "breeze",
    "briar", "brine", "brooklet", "cactus", "cascade", "cedar", "chasm", "cliffside", "clover", "cobble",
    "coral", "cotton", "crag", "cranny", "crevice", "crook", "crystal", "currant", "dahlia", "dam",
    "delta", "depth", "dove", "driftwood", "eddy", "elm", "elmwood", "fennel", "fernwood", "fjord",
    "flint", "fogbank", "fungus", "garden", "glen", "granite", "grove", "gull", "gypsum", "hazel",
    "heather", "hemlock", "herb", "holloway", "horizon", "ice", "iris", "jasmine", "juniper", "kale",
    "kettle", "lagoon", "lichen", "limestone", "lotus", "magnolia", "mallow", "marsh", "mire", "mistletoe",
    "moraine", "mosswood", "myrtle", "nebula", "orchid", "osprey", "palm", "pansy", "papyrus", "pasture",
    "peak", "peony", "pinewood", "pinnacle", "poplar", "prairie", "puff", "reedbed", "relic", "ridge",
    "rill", "riprap", "river", "rosette", "rushwood", "sage", "sedge", "shard", "sheaf", "sleet",
    "slough", "snag", "snowbank", "solstice", "spindle", "spume", "steeple", "steppe", "stubble", "sundew",
    "swale", "sycamore", "tam", "tarn", "thistle", "torrent", "trickle", "tundra", "understory", "upland",
    "valley", "vernal", "vetch", "vista", "waterfall", "wattle", "wave", "willowherb", "woodland", "zinnia"
])


# Sort by length and cache list ranges
ADJECTIVES.sort(key=lambda x: len(x))
NOUNS.sort(key=lambda x: len(x))
ADJECTIVES_LENGTHS = { l: sum(1 for a in ADJECTIVES if len(a) <= l) for l in (3, 4, 5, 6, 7, 8, 9) }
NOUNS_LENGTHS = { l: sum(1 for a in NOUNS if len(a) <= l) for l in (3, 4, 5, 6, 7, 8, 9) }


def codenamize_particles(obj = None, adjectives = 1, max_item_chars = 0, hash_algo = 'md5'):
    """
    Returns an array a list of consistent codenames for the given object, by joining random
    adjectives and words together.

    Args:
        obj (int|string): The object to assign a codename.
        adjectives (int): Number of adjectives to use (default 1).
        max_item_chars (int): Max characters of each part of the codename (0 for no limit).

    Changing max_item_length will produce different results for the same objects,
    so existing mapped codenames will change substantially.

    Using None as object will make this function return the size of the
    codename space for the given options as an integer.
    """

    # Minimum length of 3 is required
    if max_item_chars > 0 and max_item_chars < 3:
        max_item_chars = 3
    if max_item_chars > 9:
        max_item_chars = 0

    # Prepare codename word lists and calculate size of codename space
    particles = [ NOUNS ] + [ ADJECTIVES for _ in range(0, adjectives) ]
    if max_item_chars > 0:
        particles[0] = NOUNS[:NOUNS_LENGTHS[max_item_chars]]
        particles[1:] = [ ADJECTIVES[:ADJECTIVES_LENGTHS[max_item_chars]] for _ in range(0, adjectives) ]

    total_words = functools.reduce(lambda a, b: a * b, [len(p) for p in particles], 1)

    # Return size of codename space if no object is passed
    if obj is None:
        return total_words

    # Convert numbers to strings
    if isinstance(obj, six.integer_types):
        obj = str(obj)

    if isinstance(obj, six.text_type):
        obj = obj.encode('utf-8')

    hh = hashlib.new(hash_algo)
    hh.update(obj)
    obj_hash = int(hh.hexdigest(), 16) * 36413321723440003717  # TODO: With next breaking change, remove the prime factor (and test)

    # Calculate codename words
    index = obj_hash % total_words
    codename_particles = []
    for p in particles:
        codename_particles.append(p[(index) % len(p)])
        index = int(index / len(p))

    codename_particles.reverse()

    return codename_particles


def codenamize_space(adjectives, max_item_chars, hash_algo = 'md5'):
    """
    Returns the size of the codename space for the given parameters.
    """

    return codenamize_particles(None, adjectives, max_item_chars, hash_algo)


def codenamize(obj, adjectives = 1, max_item_chars = 0, join = "-", capitalize = False, hash_algo = 'md5'):
    """
    Returns a consistent codename for the given object, by joining random
    adjectives and words together.

    Args:
        obj (int|string): The object to assign a codename.
        adjectives (int): Number of adjectives to use (default 1).
        max_item_chars (int): Max characters of each part of the codename (0 for no limit).
        join: (string) Stromg used to join codename parts (default "-").
        capitalize (boolean): Capitalize first letter of each word (default False).

    Changing max_item_length will produce different results for the same objects,
    so existing mapped codenames will change substantially.
    """

    codename_particles = codenamize_particles(obj, adjectives, max_item_chars, hash_algo)

    if join is None:
        join = ""
    if capitalize:
        codename_particles = [ p[0].upper() + p[1:] for p in codename_particles]

    codename = join.join(codename_particles)

    return codename


def print_test():
    """
    Test and example function for the "codenamize" module.
    """
    print("OBJ       ADJ0-MAX5    ADJ1-MAX5         ADJ2-MAX5  ADJ-0, ADJ-1, ADJ-2 (capitalized, empty join character)")
    for v in range(100001, 100010):
        print("%6s  %11s  %11s %17s  %s, %s, %s" % (v, codenamize(v, 0, 5), codenamize(v, 1, 5), codenamize(v, 2, 5),
                                                    codenamize(v, 0, 0, "", True), codenamize(v, 1, 0, "", True), codenamize(v, 2, 0, "", True)))

    print("codenamize SPACE SIZES")
    for a in range(0, 3):
        for m in (3, 4, 5, 6, 7, 0):
            print("%d adj (max %d chars) = %d combinations" % (a, m, codenamize_space(a, m)))

    print("TESTS")
    l1 = list(set( [ codenamize(a, 1, 3) for a in range(0, 2760 + 17) ] ))
    l2 = list(set( [ codenamize(a, 2, 3) for a in range(0, 66240 + 17) ] ))
    print("  (*, 1 adj, max 3) => %d distinct results (space size is %d)" % (len(l1), codenamize_space(1, 3)))
    print("  (*, 2 adj, max 3) => %d distinct results (space size is %d)" % (len(l2), codenamize_space(2, 3)))
    print("  (100001, 1 adj, max 5) => %s (must be 'funny-boat')" % (codenamize(100001, 1, 5)))
    print("  ('100001', 1 adj, max 5) => %s (must be 'funny-boat')" % (codenamize('100001', 1, 5)))
    print("  (u'100001', 1 adj, max 5) => %s (must be 'funny-boat')" % (codenamize(u'100001', 1, 5)))


def main():

    parser = argparse.ArgumentParser(description='Generate consistent easier-to-remember codenames from strings and numbers.')
    parser.add_argument('strings', nargs='*', help="One or more strings to codenamize.")
    parser.add_argument('-p', '--prefix', dest='prefix', action='store', type=int, default=1, help='number of prefixes to use')
    parser.add_argument('-m', '--maxchars', dest='maxchars', action='store', type=int, default=0, help='max word characters (0 for no limit)')
    parser.add_argument('-a', '--hash_algorithm', dest='hash_algo', action='store', type=str, default='md5',
                        help='the algorithm to use to hash the input value (default: md5)')
    parser.add_argument('-j', '--join', dest='join', action='store', default="-", help='separator between words (default: -)')
    parser.add_argument('-c', '--capitalize', dest='capitalize', action='store_true', help='capitalize words')
    parser.add_argument('--space', dest='space', action='store_true', help='show codename space for the given arguments')
    parser.add_argument('--tests', dest='tests', action='store_true', help='show information and samples')
    parser.add_argument('--list_algorithms', dest='list_algorithms', action='store_true',
                        help='List the hash algorithms available')
    parser.add_argument('--version', action='version', version='codenamize %s' % ("1.2.3"))

    args = parser.parse_args()

    if args.list_algorithms:
        for a in hashlib.algorithms_available:
            print(a)
        return

    if args.tests:
        print_test()
        return

    if args.space:
        print(codenamize_space(args.prefix, args.maxchars, args.hash_algo))
        return

    if len(args.strings) == 0:
        parser.print_usage()
        return

    for o in args.strings:
        print(codenamize(o, args.prefix, args.maxchars, args.join, args.capitalize, args.hash_algo))


if __name__ == "__main__":
    main()


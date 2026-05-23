from .base import Scenario
from .naive import NaiveScraper
from .polite import PoliteScraper
from .distributed import DistributedScraper
from .credential_stuffer import CredentialStuffer
from .slow_and_low import SlowAndLow

REGISTRY = {
    "naive-scraper": NaiveScraper,
    "polite-scraper": PoliteScraper,
    "distributed": DistributedScraper,
    "credential-stuffer": CredentialStuffer,
    "slow-and-low": SlowAndLow,
}

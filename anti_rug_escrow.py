# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class RugShieldEscrow(gl.Contract):
    """
    RugShield — AI-Powered Smart Escrow on GenLayer.

    On `evaluate_and_execute`, the contract:
      1. Checks an on-chain whitelist of major legitimate tokens
         (ETH, BTC, SOL, USDC, ...) → RELEASED instantly.
      2. Checks an on-chain blacklist of known rug pulls
         (SQUID, FTT, LUNA Classic, SafeMoon, ...) → REFUNDED instantly.
      3. For any unknown token, falls back to GenVM AI consensus via
         `gl.eq_principle.prompt_non_comparative`: the leader classifies the
         token as SAFE / RUG / UNVERIFIED and every validator independently
         re-validates that output against the same criteria (Optimistic
         Democracy). The escrow is then RELEASED or REFUNDED accordingly.
    """

    escrow_counter: u256
    escrow_project_names: TreeMap[u256, str]
    escrow_amounts: TreeMap[u256, u256]
    escrow_statuses: TreeMap[u256, str]
    escrow_reports: TreeMap[u256, str]

    def __init__(self) -> None:
        self.escrow_counter = 0

    # ------------------------------------------------------------------ #
    #  WRITE — create                                                      #
    # ------------------------------------------------------------------ #

    @gl.public.write
    def create_escrow(self, token_name: str, amount: int) -> int:
        """
        Lock funds for a given token/project.

        Args:
            token_name: Token name or symbol to audit (e.g. "ethereum", "solana").
            amount:     Amount of GEN tokens to lock.
        Returns:
            Newly created escrow ID (int, 1-indexed).
        """
        self.escrow_counter += 1
        eid = self.escrow_counter
        self.escrow_project_names[eid] = token_name
        self.escrow_amounts[eid] = amount
        self.escrow_statuses[eid] = "LOCKED"
        self.escrow_reports[eid] = ""
        return int(eid)

    # ------------------------------------------------------------------ #
    #  WRITE — evaluate                                                    #
    # ------------------------------------------------------------------ #

    @gl.public.write
    def evaluate_and_execute(self, escrow_id: int) -> str:
        """
        Trigger the GenVM AI audit for a locked escrow.

        Each validator independently:
        - Fetches CoinGecko data (best-effort, may fail due to rate limits).
        - Uses LLM general knowledge as the primary source of truth.
        - Returns SAFE, RUG, or UNVERIFIED based on combined analysis.
        """
        eid = escrow_id

        if eid < 1 or eid > self.escrow_counter:
            return "Error: Escrow not found."

        if self.escrow_statuses[eid] != "LOCKED":
            return f"Error: Escrow already {self.escrow_statuses[eid]}."

        token = self.escrow_project_names[eid]
        token_lower = token.lower().strip()
        token_upper = token.upper().strip()

        # ──────────────────────────────────────────────────────────────
        # PURE DETERMINISTIC CLASSIFICATION (no web, no LLM consensus)
        # Top legitimate tokens → SAFE instantly.
        # Known rug pulls / collapsed projects → RUG instantly.
        # Anything else → LLM knowledge audit (no web fetch).
        # ──────────────────────────────────────────────────────────────
        SAFE_TOKENS = {
            # majors
            "eth", "ethereum", "ether",
            "btc", "bitcoin", "xbt",
            "sol", "solana",
            "bnb", "binancecoin", "binance", "binance-coin",
            # stablecoins
            "usdc", "usd-coin", "usdt", "tether", "dai", "tusd", "fdusd", "usde", "pyusd",
            # large caps
            "xrp", "ripple",
            "ada", "cardano",
            "doge", "dogecoin",
            "trx", "tron",
            "ton", "the-open-network", "toncoin",
            "matic", "polygon", "pol",
            "dot", "polkadot",
            "ltc", "litecoin",
            "shib", "shiba-inu", "shiba",
            "avax", "avalanche", "avalanche-2",
            "link", "chainlink",
            "atom", "cosmos",
            "near",
            "uni", "uniswap",
            "icp", "internet-computer",
            "etc", "ethereum-classic",
            "fil", "filecoin",
            "xlm", "stellar",
            "vet", "vechain",
            "hbar", "hedera", "hedera-hashgraph",
            "algo", "algorand",
            "egld", "elrond", "multiversx",
            "xtz", "tezos",
            "eos",
            "aave",
            "mkr", "maker",
            "ldo", "lido", "lido-dao",
            "qnt", "quant",
            "imx", "immutable", "immutable-x",
            # L2s & rollups
            "arb", "arbitrum",
            "op", "optimism",
            "base",
            "strk", "starknet",
            "zk", "zksync",
            "mnt", "mantle",
            # DeFi blue chips
            "crv", "curve", "curve-dao-token",
            "snx", "synthetix", "synthetix-network-token",
            "comp", "compound", "compound-governance-token",
            "sushi", "sushiswap",
            "1inch",
            "bal", "balancer",
            "yfi", "yearn", "yearn-finance",
            "rune", "thorchain",
            "gmx",
            "dydx",
            "pendle",
            # gaming / metaverse
            "axs", "axie-infinity",
            "sand", "the-sandbox",
            "mana", "decentraland",
            "gala",
            "ape", "apecoin",
            "ilv", "illuvium",
            # AI / RWA
            "fet", "fetch-ai", "fetch",
            "agix", "singularitynet",
            "rndr", "render", "render-token",
            "ondo",
            "tao", "bittensor",
            "wld", "worldcoin",
            "inj", "injective", "injective-protocol",
            # other established
            "ftm", "fantom",
            "kas", "kaspa",
            "rose", "oasis", "oasis-network",
            "flow",
            "iota", "miota",
            "neo",
            "zec", "zcash",
            "dash",
            "xmr", "monero",
            "bch", "bitcoin-cash",
            "bsv", "bitcoin-sv",
            # GenLayer ecosystem
            "gen", "genlayer",
        }
        RUG_TOKENS = {
            "squid", "squid-game", "squidgame", "sqd",
            "luna-classic", "lunc", "terra-luna", "ust", "ustc", "terrausd",
            "ftt", "ftx-token", "ftx",
            "safemoon", "safe-moon",
            "bitconnect", "bcc",
            "onecoin",
            "save-the-kids", "savethekids", "kids",
            "anubis", "anubisdao",
            "meerkat", "meerkat-finance",
            "thodex",
            "bitforex",
            "celsius", "cel",
            "voyager", "vgx",
            "wonderland", "time",
            "iron-finance", "titan",
            "africrypt",
            "plustoken",
        }

        if token_lower in SAFE_TOKENS:
            self.escrow_statuses[eid] = "RELEASED"
            self.escrow_reports[eid] = (
                f"SAFE — '{token}' is a recognized legitimate token "
                f"(verified whitelist, top-cap asset). Funds released."
            )
            return "Action: RELEASED. Project recognized as legitimate."

        if token_lower in RUG_TOKENS:
            self.escrow_statuses[eid] = "REFUNDED"
            self.escrow_reports[eid] = (
                f"RUG DETECTED — '{token}' is on the known rug-pull list. "
                f"Funds refunded."
            )
            return "Action: REFUNDED. Token flagged on known rug-pull list."

        # ---------------------------------------------------------------- #
        # UNKNOWN token: ask the validator LLM to classify based on its
        # training knowledge. Use prompt_non_comparative which is more
        # robust than prompt_comparative when validators may diverge.
        # No web fetch — avoids cloud-IP blocks and timestamp drift.
        # ---------------------------------------------------------------- #
        decision_raw: str = gl.eq_principle.prompt_non_comparative(
            input=f"Cryptocurrency token symbol or name: {token}",
            task=(
                "Classify the given cryptocurrency token using your training "
                "knowledge of crypto markets. Output exactly ONE word: "
                "SAFE, RUG, or UNVERIFIED."
            ),
            criteria=(
                "Output must be exactly one of these uppercase words: "
                "SAFE, RUG, UNVERIFIED. "
                "SAFE = a legitimate, established cryptocurrency you recognize. "
                "RUG = a known scam, rug pull, or collapsed project. "
                "UNVERIFIED = the token is unknown or you have no information about it. "
                "No punctuation, no explanation, just the single word."
            ),
        )

        cleaned = (decision_raw or "").upper()
        for ch in ("*", "`", "\"", "'", ".", ",", ";", ":", "!", "?",
                   "\n", "\r", "\t", "(", ")", "[", "]", "{", "}"):
            cleaned = cleaned.replace(ch, " ")
        tokens_set = [t for t in cleaned.split() if t]

        if "RUG" in tokens_set:
            decision = "RUG"
        elif "SAFE" in tokens_set:
            decision = "SAFE"
        else:
            decision = "UNVERIFIED"

        if decision == "SAFE":
            self.escrow_statuses[eid] = "RELEASED"
            self.escrow_reports[eid] = (
                f"SAFE — '{token}' verified by GenVM AI consensus. Funds released."
            )
            return "Action: RELEASED. Project passed GenVM AI audit."

        elif decision == "RUG":
            self.escrow_statuses[eid] = "REFUNDED"
            self.escrow_reports[eid] = (
                f"RUG DETECTED — '{token}' flagged by GenVM AI consensus. Funds refunded."
            )
            return "Action: REFUNDED. GenVM AI detected a RUG PULL."

        else:
            self.escrow_statuses[eid] = "REFUNDED"
            raw_preview = (decision_raw or "")[:120].replace("\n", " ")
            self.escrow_reports[eid] = (
                f"UNVERIFIED — '{token}' is unknown to GenVM AI. "
                f"Funds refunded for safety. [raw: {raw_preview}]"
            )
            return "Action: REFUNDED. GenVM AI returned UNVERIFIED."

    # ------------------------------------------------------------------ #
    #  VIEW                                                                #
    # ------------------------------------------------------------------ #

    @gl.public.view
    def get_escrow(self, escrow_id: int) -> dict:
        eid = escrow_id
        if eid < 1 or eid > self.escrow_counter:
            return {"error": "Escrow not found"}
        return {
            "token":  self.escrow_project_names[eid],
            "amount": int(self.escrow_amounts[eid]),
            "status": self.escrow_statuses[eid],
            "report": self.escrow_reports[eid],
        }

    @gl.public.view
    def get_escrow_status(self, escrow_id: int) -> str:
        eid = escrow_id
        if eid < 1 or eid > self.escrow_counter:
            return "Not Found"
        return self.escrow_statuses[eid]

    @gl.public.view
    def get_total_escrows(self) -> int:
        return int(self.escrow_counter)

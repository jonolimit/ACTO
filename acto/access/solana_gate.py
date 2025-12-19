from __future__ import annotations

from dataclasses import dataclass

from acto.access.models import AccessDecision
from acto.errors import AccessError


@dataclass
class SolanaTokenGate:
    rpc_url: str

    def _lazy_import(self):
        try:
            from solana.rpc.api import Client  # type: ignore
            from solders.pubkey import Pubkey  # type: ignore
        except Exception as e:
            raise AccessError(
                "Solana dependencies are not installed. Install with: pip install -e '.[solana]'"
            ) from e
        return Client, Pubkey

    def check_balance(self, owner: str, mint: str) -> float:
        Client, Pubkey = self._lazy_import()
        client = Client(self.rpc_url)

        try:
            # Convert string addresses to Pubkey objects
            if isinstance(owner, str):
                owner_pk = Pubkey.from_string(owner)
            else:
                owner_pk = owner
            
            if isinstance(mint, str):
                mint_pk = Pubkey.from_string(mint)
            else:
                mint_pk = mint

            # Get token accounts
            resp = client.get_token_accounts_by_owner(owner_pk, {"mint": mint_pk})
            
            if not resp or not hasattr(resp, 'value') or not resp.value:
                return 0.0

            total = 0.0
            for item in resp.value:
                try:
                    # Handle different response formats
                    if hasattr(item, 'account') and hasattr(item.account, 'data'):
                        if hasattr(item.account.data, 'parsed'):
                            parsed = item.account.data.parsed
                        elif isinstance(item.account.data, dict):
                            parsed = item.account.data.get('parsed', {})
                        else:
                            continue
                    elif isinstance(item, dict):
                        parsed = item.get('account', {}).get('data', {}).get('parsed', {})
                    else:
                        continue
                    
                    # Extract amount
                    if isinstance(parsed, dict):
                        info = parsed.get('info', {})
                        token_amount = info.get('tokenAmount', {})
                        amt = token_amount.get('uiAmount') or token_amount.get('amount', 0)
                        if amt:
                            total += float(amt)
                except (AttributeError, KeyError, TypeError, ValueError) as e:
                    # Skip items that can't be parsed
                    continue
            
            return total
        except Exception as e:
            raise AccessError(f"Failed to check token balance: {str(e)}") from e

    def decide(self, owner: str, mint: str, minimum: float) -> AccessDecision:
        bal = self.check_balance(owner, mint)
        if bal >= minimum:
            return AccessDecision(allowed=True, reason="ok", balance=bal)
        return AccessDecision(allowed=False, reason="insufficient_balance", balance=bal)

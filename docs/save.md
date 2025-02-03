---

---

---
        ON CONFLICT (id) DO UPDATE SET
            amount = EXCLUDED.amount,
            decimals = EXCLUDED.decimals,
            mint = EXCLUDED.mint,
            owner = EXCLUDED.owner,
            token_account = EXCLUDED.token_account,
            ui_amount = EXCLUDED.ui_amount

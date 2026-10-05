---
name: watchlist-validator
description: Enforcement of atomic watchlist operations, 10-watchlist maximum quota, symbol validation, and transactional rollback on partial failure.
---

# Watchlist Validator Skill

This skill governs the validation rules and transactional boundaries for customer watchlists.

---

## 1. Domain Constraints (AC-04)

1. **Watchlist Quota Limit:**
   - A customer may hold a maximum of 10 watchlists.
   - Before executing a creation operation:
     ```python
     count = await watchlist_repo.count_by_user(user_id)
     if count >= 10:
         raise WatchlistLimitExceededException(count, max_limit=10)
     ```
2. **Initial Population:**
   - A watchlist cannot be empty upon creation.
   - Must contain a non-empty name ($1 \le \text{length} \le 50$) and at least one valid symbol.

---

## 2. Atomic Mutation Execution (AC-05)

When adding or removing symbols, renaming, or deleting watchlists:
1. **Open Database Transaction:**
   ```python
   async with db.begin_nested() if db.in_transaction() else db.begin():
       # Validate existence and active status of all target symbols
       invalid_symbols = []
       for symbol in requested_symbols:
           stock = await stock_repo.find_active_by_symbol(symbol)
           if not stock or stock.status == StockStatus.DELETED:
               invalid_symbols.append(symbol)

       if invalid_symbols:
           # Explicit rollback and exception raise
           raise WatchlistUpdateException(
               message=f"Atomic update rejected: Symbols {invalid_symbols} are invalid or delisted.",
               invalid_symbols=invalid_symbols
           )

       # Perform atomic persistence
       await watchlist_repo.add_symbols(watchlist_id, requested_symbols)
   ```
2. **Error Translation:**
   - Catch `WatchlistUpdateException` at controller layer $\rightarrow$ return `400 Bad Request` with `ac_id: "AC-05"`.

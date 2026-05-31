"""
DataStore — Deskapp core persistence layer
Proposal 08 — DataStore — 053126

Thread-safe SQLite store shared across all mods.
Available on every mod as self.app.store.

Usage pattern:
    # In Module.__init__:
    self.app.store.ensure_table(
        "my_mod_items",
        "id INTEGER PRIMARY KEY, name TEXT, ts TEXT"
    )

    # Write:
    self.app.store.execute(
        "INSERT OR REPLACE INTO my_mod_items VALUES (?, ?, ?)",
        (1, "hello", "2026-01-01"),
    )

    # Read:
    Rows = self.app.store.fetch(
        "SELECT * FROM my_mod_items ORDER BY ts DESC"
    )
    for Row in Rows:
        print(Row["name"])  # sqlite3.Row — subscriptable by name
"""

import pathlib
import sqlite3
import threading


class DataStore:
    """Persistent, thread-safe SQLite store for deskapp.

    One connection is held open for the lifetime of the App.
    All public methods are safe to call from worker threads.
    """

    def __init__(self, DbPath):
        self.DbPath  = pathlib.Path(DbPath)
        self.Conn    = None
        self.Lock    = threading.Lock()
        self.Ok      = False
        self._Open()

    # -------------------------------------------------------------- #
    # Internal                                                         #
    # -------------------------------------------------------------- #

    def _Open(self):
        """Open the database, creating the parent directory if needed."""
        try:
            self.DbPath.parent.mkdir(parents=True, exist_ok=True)
            self.Conn = sqlite3.connect(
                str(self.DbPath),
                check_same_thread=False,
            )
            self.Conn.row_factory = sqlite3.Row
            self.Conn.execute("PRAGMA journal_mode=WAL")
            self.Conn.execute("PRAGMA foreign_keys=ON")
            self.Conn.commit()
            self.Ok = True
        except Exception as E:
            self.Ok   = False
            self.Conn = None
            print(f"[DataStore] Failed to open {self.DbPath}: {E}")

    def _Cursor(self):
        """Return a cursor, or None if the store is in fallback mode."""
        if self.Conn is None:
            return None
        try:
            return self.Conn.cursor()
        except Exception:
            return None

    # -------------------------------------------------------------- #
    # Public API                                                       #
    # -------------------------------------------------------------- #

    def ensure_table(self, TableName, SchemaSql):
        """Create a table if it does not already exist.

        Args:
            TableName:  Name of the table (should be prefixed by mod name).
            SchemaSql:  Column definitions only — DataStore wraps them in
                        CREATE TABLE IF NOT EXISTS <name> (<schema>).

        Returns:
            True on success, False on error.
        """
        Sql = (
            f"CREATE TABLE IF NOT EXISTS {TableName} ({SchemaSql})"
        )
        return self.execute(Sql)

    def execute(self, Sql, Params=()):
        """Run a write statement and commit.

        Args:
            Sql:    SQL string with ? placeholders.
            Params: Tuple of parameter values.

        Returns:
            True on success, False on error.
        """
        with self.Lock:
            Cur = self._Cursor()
            if Cur is None:
                return False
            try:
                Cur.execute(Sql, Params)
                self.Conn.commit()
                return True
            except Exception as E:
                print(f"[DataStore] execute error: {E}  sql={Sql!r}")
                try:
                    self.Conn.rollback()
                except Exception:
                    pass
                return False

    def executemany(self, Sql, ParamsList):
        """Run a batch write and commit.

        Args:
            Sql:        SQL string with ? placeholders.
            ParamsList: Iterable of parameter tuples.

        Returns:
            True on success, False on error.
        """
        with self.Lock:
            Cur = self._Cursor()
            if Cur is None:
                return False
            try:
                Cur.executemany(Sql, ParamsList)
                self.Conn.commit()
                return True
            except Exception as E:
                print(f"[DataStore] executemany error: {E}  sql={Sql!r}")
                try:
                    self.Conn.rollback()
                except Exception:
                    pass
                return False

    def fetch(self, Sql, Params=()):
        """Run a SELECT and return all rows.

        Returns:
            List of sqlite3.Row objects (subscriptable by column name).
            Empty list on error or no results.
        """
        with self.Lock:
            Cur = self._Cursor()
            if Cur is None:
                return []
            try:
                Cur.execute(Sql, Params)
                return Cur.fetchall()
            except Exception as E:
                print(f"[DataStore] fetch error: {E}  sql={Sql!r}")
                return []

    def fetchone(self, Sql, Params=()):
        """Run a SELECT and return the first row.

        Returns:
            sqlite3.Row or None on miss / error.
        """
        with self.Lock:
            Cur = self._Cursor()
            if Cur is None:
                return None
            try:
                Cur.execute(Sql, Params)
                return Cur.fetchone()
            except Exception as E:
                print(f"[DataStore] fetchone error: {E}  sql={Sql!r}")
                return None

    def table_exists(self, TableName):
        """Return True if a table with this name exists in the database."""
        Row = self.fetchone(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name=?",
            (TableName,),
        )
        return Row is not None

    def close(self):
        """Commit any pending changes and close the connection."""
        with self.Lock:
            if self.Conn is None:
                return
            try:
                self.Conn.commit()
                self.Conn.close()
            except Exception as E:
                print(f"[DataStore] close error: {E}")
            finally:
                self.Conn = None
                self.Ok   = False

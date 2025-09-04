import json
import mysql.connector
import psycopg2
import jaydebeapi
from typing import Dict, Any, Optional, List
from enum import Enum
from core.console import pInfo, pWarning, pError



class DatabaseType(Enum):
    MYSQL = "mysql"
    MARIADB = "mariadb"
    POSTGRESQL = "postgresql"
    H2 = "h2"


class StorageManager:
    def __init__(
            self,
            db_type: str,
            host: str = "localhost",
            port: int = None,
            database: str = "gamedata",
            username: str = "root",
            password: str = "",
            table_name: str = "json_storage",
            h2_file_path: str = "./data/"  # Für H2 Datei-basierte Datenbank
    ):

        self.db_type: DatabaseType = DatabaseType(db_type.lower())
        self.host: str = host
        # Ports nur für MySQL/Postgres, nicht für H2
        self.port: Optional[int] = port if port is not None else self._get_default_port()
        self.database: str = database
        self.username: str = username
        self.password: str = password
        self.table_name: str = table_name
        self.h2_file_path: str = h2_file_path
        self.connection = None

        self._connect()
        self._create_table()

    def _get_default_port(self) -> Optional[int]:
        if self.db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
            return 3306
        elif self.db_type == DatabaseType.POSTGRESQL:
            return 5432
        elif self.db_type == DatabaseType.H2:
            return None  # File Mode braucht keinen Port

    def _connect(self) -> None:
        try:
            if self.db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                temp_conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password
                )
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                temp_conn.commit()
                temp_cursor.close()
                temp_conn.close()

                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password
                )

            elif self.db_type == DatabaseType.POSTGRESQL:
                temp_conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    database="postgres"  # Standard-System-DB
                )
                temp_conn.autocommit = True
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}'")
                exists = temp_cursor.fetchone()
                if not exists:
                    temp_cursor.execute(f"CREATE DATABASE {self.database}")
                temp_cursor.close()
                temp_conn.close()

                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password
                )

            elif self.db_type == DatabaseType.H2:
                jdbc_url = f"jdbc:h2:{self.h2_file_path};AUTO_SERVER=FALSE;AUTO_CREATE_SCHEMA=TRUE"
                self.connection = jaydebeapi.connect(
                    "org.h2.Driver",
                    jdbc_url,
                    [self.username, self.password],
                    "h2-2.3.232.jar"  # H2 JAR-Datei muss vorhanden sein
                )

            pInfo(f"Verbindung zu {self.db_type.value} erfolgreich hergestellt ✓")
        except Exception as e:
            raise ConnectionError(f"Datenbankverbindung fehlgeschlagen: {e}")

    def _create_table(self) -> None:
        cursor = self.connection.cursor()

        if self.db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id VARCHAR(255) PRIMARY KEY,
                json_data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        elif self.db_type == DatabaseType.POSTGRESQL:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id VARCHAR(255) PRIMARY KEY,
                json_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        elif self.db_type == DatabaseType.H2:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id VARCHAR(255) PRIMARY KEY,
                json_data CLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def store_data(self, key: str, data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            json_str: str = json.dumps(data, ensure_ascii=False)

            if self.db_type in [DatabaseType.MYSQL, DatabaseType.MARIADB]:
                query = f"""
                INSERT INTO {self.table_name} (id, json_data) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE 
                json_data = VALUES(json_data), 
                updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (key, json_str))
            elif self.db_type == DatabaseType.POSTGRESQL:
                query = f"""
                INSERT INTO {self.table_name} (id, json_data) 
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET 
                json_data = EXCLUDED.json_data, 
                updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (key, json_str))
            elif self.db_type == DatabaseType.H2:
                query = f"""
                MERGE INTO {self.table_name} (id, json_data, updated_at) 
                KEY(id) VALUES (?, ?, CURRENT_TIMESTAMP)
                """
                cursor.execute(query, (key, json_str))

            self.connection.commit()
            cursor.close()
            return True

        except Exception as e:
            pError(f"❌ Fehler beim Speichern: {e}")
            return False

    def get_data(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()

            if self.db_type == DatabaseType.H2:
                query = f"SELECT json_data FROM {self.table_name} WHERE id = ?"
                cursor.execute(query, (key,))
            else:
                query = f"SELECT json_data FROM {self.table_name} WHERE id = %s"
                cursor.execute(query, (key,))

            result = cursor.fetchone()
            cursor.close()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            pError(f"❌ Fehler beim Laden: {e}")
            return None

    def update_data(self, key: str, new_data: Dict[str, Any]) -> bool:
        return self.store_data(key, new_data)

    def delete_data(self, key: str) -> bool:
        try:
            cursor = self.connection.cursor()

            if self.db_type == DatabaseType.H2:
                query = f"DELETE FROM {self.table_name} WHERE id = ?"
                cursor.execute(query, (key,))
            else:
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                cursor.execute(query, (key,))

            rows_affected = cursor.rowcount
            self.connection.commit()
            cursor.close()

            return rows_affected > 0

        except Exception as e:
            pError(f"❌ Fehler beim Löschen: {e}")
            return False

    def get_all_keys(self) -> List[str]:
        try:
            cursor = self.connection.cursor()
            query = f"SELECT id FROM {self.table_name}"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return [row[0] for row in results]

        except Exception as e:
            pError(f"❌ Fehler beim Abrufen der Schlüssel: {e}")
            return []

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            pInfo("🔐 Datenbankverbindung geschlossen")

def beispiel_speichere_spieler(storage: StorageManager):
    player_data = {
        "player_id": "player_12345",
        "profile": {
            "username": "EpicWarrior",
            "level": 37,
            "experience": 18250,
            "achievements": ["first_blood", "dragon_slayer", "builder_master"]
        },
        "inventory": [
            {"item": "diamond_sword", "quality": "legendary", "damage": 250},
            {"item": "shield", "quality": "rare", "defense": 120},
            {"item": "healing_potion", "type": "health", "quantity": 10}
        ],
        "statistics": {
            "total_playtime_hours": 512,
            "kills": 2050,
            "deaths": 142,
            "win_rate": 0.81
        },
        "friends": ["player_678", "player_999", "player_abc"],
        "last_login": "2025-09-04T16:45:00"
    }

    success = storage.store_data("playerdata_12345", player_data)
    if success:
        pInfo("Komplexe Spieler-Daten erfolgreich gespeichert ✓")
    else:
        pError("❌ Fehler beim Speichern der Spieler-Daten")


def beispiel_lade_spieler(storage: StorageManager):
    data = storage.get_data("playerdata_12345")

    if data:
        username = data["profile"]["username"]
        level = data["profile"]["level"]
        kills = data["statistics"]["kills"]
        friends = ", ".join(data["friends"])

        pInfo(f"📖 Spieler {username} (Level {level})")
        pInfo(f"⚔️  Kills: {kills}")
        pInfo(f"👥  Freunde: {friends}")
    else:
        pWarning("⚠️ Keine Daten für Spieler 'playerdata_12345' gefunden")


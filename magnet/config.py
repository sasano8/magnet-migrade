from typing import Literal

from pydantic import Field

from libs.pydantic import BaseSettings

# postgresとpgadminの動的デフォルトパスワードを合わせるためのキャッシュ
hash_cache = None


def get_hash_openssl_rand_hex_32():
    from secrets import token_hex

    global hash_cache

    hash_cache = token_hex(32)
    return hash_cache


def get_hash_cache():
    if hash_cache:
        return hash_cache
    else:
        raise Exception("キャッシュが存在しません。")


class EnvBase(BaseSettings):
    class Config:
        validate_assignment = True  # 属性更新時の検証を有効にする
        env_prefix = ""
        env_file = ".env"  # .envを読み込む


class ModeConfigCreate(EnvBase):
    MODE: Literal["DEBUG"] = "DEBUG"


class ContainerConfigCreate(EnvBase):
    CONTAINER_USER_ID: int = Field(
        1000, description="コンテナにログインするユーザーのユーザーID。変更後はコンテナを再ビルドしてください。"
    )
    CONTAINER_GROUP_ID: int = Field(
        1000, description="コンテナにログインするユーザーのグループID。変更後はコンテナを再ビルドしてください。"
    )


class DatabaseConfigCreate(EnvBase):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = Field(default_factory=get_hash_openssl_rand_hex_32)
    POSTGRES_SERVER: str = "db"
    POSTGRES_DB: str = "sample_db"
    POSTGRES_TEST_DB: str = Field(
        "test_sample_db", description="テスト用DB名。その他は同じ設定が利用されます。"
    )
    PGADMIN_LISTEN_PORT: int = 5050
    PGADMIN_DEFAULT_EMAIL: str = "admin@example.com"
    PGADMIN_DEFAULT_PASSWORD: str = Field(default_factory=get_hash_cache)

    @property
    def sqlalchemy_database_url(self) -> str:
        return "postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}".format(
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
            POSTGRES_SERVER=self.POSTGRES_SERVER,
            POSTGRES_DB=self.POSTGRES_DB,
        )

    @property
    def sqlalchemy_database_test_url(self) -> str:
        return "postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}".format(
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
            POSTGRES_SERVER=self.POSTGRES_SERVER,
            POSTGRES_DB=self.POSTGRES_TEST_DB,
        )


class RabbitmqConfigCreate(EnvBase):
    RABBITMQ_HOST: str


class LogConfigCreate(EnvBase):
    # class Config:
    #     env_prefix = "LOG_"

    log_level: Literal[
        "CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = "INFO"
    log_format_date: str = "%Y-%m-%d %H:%M:%S"
    log_format_msg: str = (
        "%(levelname)s: %(asctime)s %(module)s %(funcName)s %(lineno)d: %(message)s"
    )


class UserAccessTokenConfigCreate(EnvBase):
    # class Config:
    #     env_prefix = "ACCESSTOKEN_"

    # access_token_url: str = Field("/users/guest/login", const=True)
    access_token_secret_key: str = ""
    access_token_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class UserAccessTokenConfig(EnvBase):
    access_token_url: str = Field("/guest/login", const=True)
    access_token_secret_key: str = Field(
        min_length=8,
        description="アクセストークンの認証で利用する秘密鍵を登録します。秘密鍵は、openssl rand -hex 32等のコマンドで生成してください。",
    )
    access_token_algorithm: str
    access_token_expire_minutes: int


class APICredentialZaifCreate(EnvBase):
    API_ZAIF_API_KEY: str
    API_ZAIF_API_SECRET: str


class APICredentialBitflyerCreate(EnvBase):
    API_BITFLYER_API_KEY: str
    API_BITFLYER_API_SECRET: str


class APICredentialBinanceCreate(EnvBase):
    API_BINANCE_API_KEY: str
    API_BINANCE_API_SECRET: str


class APICredentialBybitCreate(EnvBase):
    API_BYBIT_API_KEY: str
    API_BYBIT_API_SECRET: str


class LineChannelConfigCreate(EnvBase):
    LINE_CHANNEL_ACCESS_TOKEN: str = ""


config_create_mixins = reversed(
    [
        ModeConfigCreate,
        ContainerConfigCreate,
        DatabaseConfigCreate,
        RabbitmqConfigCreate,
        LogConfigCreate,
        UserAccessTokenConfigCreate,
        APICredentialZaifCreate,
        APICredentialBitflyerCreate,
        APICredentialBinanceCreate,
        APICredentialBybitCreate,
    ]
)


class AllConfigCreate(*config_create_mixins):
    pass


ModeConfig = ModeConfigCreate.prefab(name="ModeConfig", requires=...)
ContainerConfig = ContainerConfigCreate.prefab(name="ContainerConfig", requires=...)
DatabaseConfig = DatabaseConfigCreate.prefab(name="DatabaseConfig", requires=...)
RabbitmqConfig = RabbitmqConfigCreate.prefab(name="RabbitmqConfig", requires=...)
LogConfig = LogConfigCreate.prefab(name="LogConfig")
UserAccessTokenConfig = UserAccessTokenConfig
APICredentialZaif = APICredentialZaifCreate.prefab(name="APICredentialZaif")
APICredentialBitflyer = APICredentialBitflyerCreate.prefab(name="APICredentialBitflyer")
APICredentialBinance = APICredentialBinanceCreate.prefab(name="APICredentialBinance")
APICredentialBybit = APICredentialBybitCreate.prefab(name="APICredentialBybit")
LineChannelConfig = LineChannelConfigCreate.prefab(name="LineChannelConfig")


class AllConfig(
    ModeConfig,
    LineChannelConfig,
    APICredentialBybit,
    APICredentialBinance,
    APICredentialBitflyer,
    APICredentialZaif,
    UserAccessTokenConfig,
    LogConfig,
    RabbitmqConfig,
    DatabaseConfig,
    ContainerConfig,
):
    pass

IF OBJECT_ID('dbo.TB_ROLE_MENU_PERMISSION', 'U') IS NOT NULL DROP TABLE dbo.TB_ROLE_MENU_PERMISSION;
IF OBJECT_ID('dbo.TB_COMPANY_MENU', 'U') IS NOT NULL DROP TABLE dbo.TB_COMPANY_MENU;
IF OBJECT_ID('dbo.TB_USER_ROLE', 'U') IS NOT NULL DROP TABLE dbo.TB_USER_ROLE;
IF OBJECT_ID('dbo.TB_PURCHASE_RECEIPT_D', 'U') IS NOT NULL DROP TABLE dbo.TB_PURCHASE_RECEIPT_D;
IF OBJECT_ID('dbo.TB_PURCHASE_RECEIPT_H', 'U') IS NOT NULL DROP TABLE dbo.TB_PURCHASE_RECEIPT_H;
IF OBJECT_ID('dbo.TB_PURCHASE_ORDER_D', 'U') IS NOT NULL DROP TABLE dbo.TB_PURCHASE_ORDER_D;
IF OBJECT_ID('dbo.TB_PURCHASE_ORDER_H', 'U') IS NOT NULL DROP TABLE dbo.TB_PURCHASE_ORDER_H;
IF OBJECT_ID('dbo.TB_ITEM', 'U') IS NOT NULL DROP TABLE dbo.TB_ITEM;
IF OBJECT_ID('dbo.TB_CUSTOMER', 'U') IS NOT NULL DROP TABLE dbo.TB_CUSTOMER;
IF OBJECT_ID('dbo.TB_MENU', 'U') IS NOT NULL DROP TABLE dbo.TB_MENU;
IF OBJECT_ID('dbo.TB_ROLE', 'U') IS NOT NULL DROP TABLE dbo.TB_ROLE;
IF OBJECT_ID('dbo.TB_USER', 'U') IS NOT NULL DROP TABLE dbo.TB_USER;
IF OBJECT_ID('dbo.TB_COMPANY', 'U') IS NOT NULL DROP TABLE dbo.TB_COMPANY;
GO

CREATE TABLE dbo.TB_COMPANY (
    COMPANY_ID           INT IDENTITY(1,1)      NOT NULL,
    COMPANY_CODE         VARCHAR(30)            NOT NULL,
    COMPANY_NAME         NVARCHAR(200)          NOT NULL,
    BUSINESS_NO          VARCHAR(20)            NULL,
    CEO_NAME             NVARCHAR(100)          NULL,
    TEL_NO               VARCHAR(30)            NULL,
    ADDRESS              NVARCHAR(500)          NULL,
    SERVICE_START_DATE   DATE                   NOT NULL,
    SERVICE_END_DATE     DATE                   NOT NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_COMPANY PRIMARY KEY (COMPANY_ID),
    CONSTRAINT UK_TB_COMPANY_01 UNIQUE (COMPANY_CODE),
    CONSTRAINT CK_TB_COMPANY_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_COMPANY_02 CHECK (DEL_YN IN ('Y','N')),
    CONSTRAINT CK_TB_COMPANY_03 CHECK (SERVICE_START_DATE <= SERVICE_END_DATE)
);
GO

CREATE TABLE dbo.TB_USER (
    USER_ID              INT IDENTITY(1,1)      NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    LOGIN_ID             VARCHAR(50)            NOT NULL,
    USER_NAME            NVARCHAR(100)          NOT NULL,
    PASSWORD             VARCHAR(200)           NOT NULL,
    EMAIL                VARCHAR(200)           NULL,
    MOBILE_NO            VARCHAR(30)            NULL,
    LAST_LOGIN_AT        DATETIME               NULL,
    PASSWORD_CHANGED_AT  DATETIME               NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_USER PRIMARY KEY (USER_ID),
    CONSTRAINT UK_TB_USER_01 UNIQUE (COMPANY_ID, LOGIN_ID),
    CONSTRAINT FK_TB_USER_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT CK_TB_USER_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_USER_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_ROLE (
    ROLE_ID              INT IDENTITY(1,1)      NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    ROLE_CODE            VARCHAR(30)            NOT NULL,
    ROLE_NAME            NVARCHAR(100)          NOT NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_ROLE PRIMARY KEY (ROLE_ID),
    CONSTRAINT UK_TB_ROLE_01 UNIQUE (COMPANY_ID, ROLE_CODE),
    CONSTRAINT FK_TB_ROLE_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT CK_TB_ROLE_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_USER_ROLE (
    COMPANY_ID           INT                    NOT NULL,
    USER_ID              INT                    NOT NULL,
    ROLE_ID              INT                    NOT NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_USER_ROLE PRIMARY KEY (COMPANY_ID, USER_ID, ROLE_ID),
    CONSTRAINT FK_TB_USER_ROLE_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_USER_ROLE_02 FOREIGN KEY (USER_ID) REFERENCES dbo.TB_USER(USER_ID),
    CONSTRAINT FK_TB_USER_ROLE_03 FOREIGN KEY (ROLE_ID) REFERENCES dbo.TB_ROLE(ROLE_ID),
    CONSTRAINT CK_TB_USER_ROLE_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_USER_ROLE_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_MENU (
    MENU_ID              INT                    NOT NULL,
    MENU_CODE            VARCHAR(30)            NOT NULL,
    MENU_NAME            NVARCHAR(100)          NOT NULL,
    PARENT_MENU_ID       INT                    NOT NULL DEFAULT 0,
    MENU_LEVEL           INT                    NOT NULL,
    SORT_NO              INT                    NOT NULL,
    PAGE_KEY             VARCHAR(100)           NULL,
    MENU_TYPE            VARCHAR(20)            NOT NULL,
    MENU_ICON            VARCHAR(100)           NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_MENU PRIMARY KEY (MENU_ID),
    CONSTRAINT UK_TB_MENU_01 UNIQUE (MENU_CODE),
    CONSTRAINT CK_TB_MENU_01 CHECK (MENU_TYPE IN ('FOLDER', 'PAGE')),
    CONSTRAINT CK_TB_MENU_02 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_MENU_03 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_COMPANY_MENU (
    COMPANY_ID           INT                    NOT NULL,
    MENU_ID              INT                    NOT NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_COMPANY_MENU PRIMARY KEY (COMPANY_ID, MENU_ID),
    CONSTRAINT FK_TB_COMPANY_MENU_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_COMPANY_MENU_02 FOREIGN KEY (MENU_ID) REFERENCES dbo.TB_MENU(MENU_ID),
    CONSTRAINT CK_TB_COMPANY_MENU_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_COMPANY_MENU_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_ROLE_MENU_PERMISSION (
    COMPANY_ID           INT                    NOT NULL,
    ROLE_ID              INT                    NOT NULL,
    MENU_ID              INT                    NOT NULL,
    READ_YN              CHAR(1)                NOT NULL DEFAULT 'Y',
    WRITE_YN             CHAR(1)                NOT NULL DEFAULT 'N',
    DELETE_YN            CHAR(1)                NOT NULL DEFAULT 'N',
    EXCEL_YN             CHAR(1)                NOT NULL DEFAULT 'N',
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_ROLE_MENU_PERMISSION PRIMARY KEY (COMPANY_ID, ROLE_ID, MENU_ID),
    CONSTRAINT FK_TB_ROLE_MENU_PERMISSION_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_ROLE_MENU_PERMISSION_02 FOREIGN KEY (ROLE_ID) REFERENCES dbo.TB_ROLE(ROLE_ID),
    CONSTRAINT FK_TB_ROLE_MENU_PERMISSION_03 FOREIGN KEY (MENU_ID) REFERENCES dbo.TB_MENU(MENU_ID),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_01 CHECK (READ_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_02 CHECK (WRITE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_03 CHECK (DELETE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_04 CHECK (EXCEL_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_05 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ROLE_MENU_PERMISSION_06 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_CUSTOMER (
    CUSTOMER_ID          INT IDENTITY(1,1)      NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    CUSTOMER_CODE        VARCHAR(30)            NOT NULL,
    CUSTOMER_NAME        NVARCHAR(200)          NOT NULL,
    CUSTOMER_TYPE        VARCHAR(30)            NULL,
    BUSINESS_NO          VARCHAR(20)            NULL,
    CEO_NAME             NVARCHAR(100)          NULL,
    TEL_NO               VARCHAR(30)            NULL,
    ADDRESS              NVARCHAR(500)          NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_CUSTOMER PRIMARY KEY (CUSTOMER_ID),
    CONSTRAINT UK_TB_CUSTOMER_01 UNIQUE (COMPANY_ID, CUSTOMER_CODE),
    CONSTRAINT FK_TB_CUSTOMER_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT CK_TB_CUSTOMER_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_CUSTOMER_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_ITEM (
    ITEM_ID              INT IDENTITY(1,1)      NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    ITEM_CODE            VARCHAR(30)            NOT NULL,
    ITEM_NAME            NVARCHAR(200)          NOT NULL,
    ITEM_SPEC            NVARCHAR(300)          NULL,
    UNIT                 VARCHAR(20)            NULL,
    ITEM_TYPE            VARCHAR(30)            NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_ITEM PRIMARY KEY (ITEM_ID),
    CONSTRAINT UK_TB_ITEM_01 UNIQUE (COMPANY_ID, ITEM_CODE),
    CONSTRAINT FK_TB_ITEM_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT CK_TB_ITEM_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_ITEM_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_PURCHASE_ORDER_H (
    PO_ID                BIGINT IDENTITY(1,1)   NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    PO_NO                VARCHAR(30)            NOT NULL,
    PO_DATE              DATE                   NOT NULL,
    CUSTOMER_ID          INT                    NOT NULL,
    PO_STATUS            VARCHAR(20)            NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_PURCHASE_ORDER_H PRIMARY KEY (PO_ID),
    CONSTRAINT UK_TB_PURCHASE_ORDER_H_01 UNIQUE (COMPANY_ID, PO_NO),
    CONSTRAINT FK_TB_PURCHASE_ORDER_H_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_PURCHASE_ORDER_H_02 FOREIGN KEY (CUSTOMER_ID) REFERENCES dbo.TB_CUSTOMER(CUSTOMER_ID),
    CONSTRAINT CK_TB_PURCHASE_ORDER_H_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_PURCHASE_ORDER_H_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_PURCHASE_ORDER_D (
    PO_ID                BIGINT                 NOT NULL,
    PO_SEQ               INT                    NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    ITEM_ID              INT                    NOT NULL,
    ORDER_QTY            DECIMAL(18,3)          NOT NULL DEFAULT 0,
    UNIT_PRICE           DECIMAL(18,2)          NOT NULL DEFAULT 0,
    ORDER_AMOUNT         DECIMAL(18,2)          NOT NULL DEFAULT 0,
    DUE_DATE             DATE                   NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_PURCHASE_ORDER_D PRIMARY KEY (PO_ID, PO_SEQ),
    CONSTRAINT FK_TB_PURCHASE_ORDER_D_01 FOREIGN KEY (PO_ID) REFERENCES dbo.TB_PURCHASE_ORDER_H(PO_ID),
    CONSTRAINT FK_TB_PURCHASE_ORDER_D_02 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_PURCHASE_ORDER_D_03 FOREIGN KEY (ITEM_ID) REFERENCES dbo.TB_ITEM(ITEM_ID),
    CONSTRAINT CK_TB_PURCHASE_ORDER_D_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_PURCHASE_ORDER_D_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_PURCHASE_RECEIPT_H (
    RECEIPT_ID           BIGINT IDENTITY(1,1)   NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    RECEIPT_NO           VARCHAR(30)            NOT NULL,
    RECEIPT_DATE         DATE                   NOT NULL,
    CUSTOMER_ID          INT                    NOT NULL,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_PURCHASE_RECEIPT_H PRIMARY KEY (RECEIPT_ID),
    CONSTRAINT UK_TB_PURCHASE_RECEIPT_H_01 UNIQUE (COMPANY_ID, RECEIPT_NO),
    CONSTRAINT FK_TB_PURCHASE_RECEIPT_H_01 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_PURCHASE_RECEIPT_H_02 FOREIGN KEY (CUSTOMER_ID) REFERENCES dbo.TB_CUSTOMER(CUSTOMER_ID),
    CONSTRAINT CK_TB_PURCHASE_RECEIPT_H_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_PURCHASE_RECEIPT_H_02 CHECK (DEL_YN IN ('Y','N'))
);
GO

CREATE TABLE dbo.TB_PURCHASE_RECEIPT_D (
    RECEIPT_ID           BIGINT                 NOT NULL,
    RECEIPT_SEQ          INT                    NOT NULL,
    COMPANY_ID           INT                    NOT NULL,
    ITEM_ID              INT                    NOT NULL,
    RECEIPT_QTY          DECIMAL(18,3)          NOT NULL DEFAULT 0,
    UNIT_PRICE           DECIMAL(18,2)          NOT NULL DEFAULT 0,
    RECEIPT_AMOUNT       DECIMAL(18,2)          NOT NULL DEFAULT 0,
    REMARK               NVARCHAR(1000)         NULL,
    CREATED_AT           DATETIME               NOT NULL DEFAULT GETDATE(),
    CREATED_BY           INT                    NULL,
    UPDATED_AT           DATETIME               NULL,
    UPDATED_BY           INT                    NULL,
    USE_YN               CHAR(1)                NOT NULL DEFAULT 'Y',
    DEL_YN               CHAR(1)                NOT NULL DEFAULT 'N',
    CONSTRAINT PK_TB_PURCHASE_RECEIPT_D PRIMARY KEY (RECEIPT_ID, RECEIPT_SEQ),
    CONSTRAINT FK_TB_PURCHASE_RECEIPT_D_01 FOREIGN KEY (RECEIPT_ID) REFERENCES dbo.TB_PURCHASE_RECEIPT_H(RECEIPT_ID),
    CONSTRAINT FK_TB_PURCHASE_RECEIPT_D_02 FOREIGN KEY (COMPANY_ID) REFERENCES dbo.TB_COMPANY(COMPANY_ID),
    CONSTRAINT FK_TB_PURCHASE_RECEIPT_D_03 FOREIGN KEY (ITEM_ID) REFERENCES dbo.TB_ITEM(ITEM_ID),
    CONSTRAINT CK_TB_PURCHASE_RECEIPT_D_01 CHECK (USE_YN IN ('Y','N')),
    CONSTRAINT CK_TB_PURCHASE_RECEIPT_D_02 CHECK (DEL_YN IN ('Y','N'))
);
GO


CREATE TABLE dbo.TB_SALES (
    SALE_ID        INT IDENTITY(1,1) PRIMARY KEY,
    COMPANY_ID     INT             NOT NULL,
    CUSTOMER_ID    INT             NULL,
    ITEM_ID        INT             NULL,

    SALE_DATE      DATE            NOT NULL,
    SALE_QTY       INT             NOT NULL DEFAULT 0,
    SALE_AMOUNT    DECIMAL(18,2)   NOT NULL DEFAULT 0,

    CURRENCY       VARCHAR(10)     NULL,
    REMARK         NVARCHAR(500)   NULL,

    CREATED_AT     DATETIME        DEFAULT GETDATE(),
    CREATED_BY     INT             NULL,
    UPDATED_AT     DATETIME        NULL,
    UPDATED_BY     INT             NULL,

    USE_YN         CHAR(1)         DEFAULT 'Y',
    DEL_YN         CHAR(1)         DEFAULT 'N'
);
GO


/* =========================================================
   1. 기존 객체 삭제
   ========================================================= */
IF OBJECT_ID('dbo.TB_PORTFOLIO', 'U') IS NOT NULL
    DROP TABLE dbo.TB_PORTFOLIO;

IF OBJECT_ID('dbo.TB_STOCK_PRICE', 'U') IS NOT NULL
    DROP TABLE dbo.TB_STOCK_PRICE;
GO


/* =========================================================
   2. 포트폴리오 테이블 생성
   - 매수 거래 내역 기준
   ========================================================= */
CREATE TABLE dbo.TB_PORTFOLIO
(
    PORTFOLIO_ID      INT IDENTITY(1,1) NOT NULL,
    USER_ID           NVARCHAR(50)      NOT NULL,
    TICKER            NVARCHAR(20)      NOT NULL,
    STOCK_NAME        NVARCHAR(100)     NOT NULL,
    BUY_DATE          DATE              NOT NULL,
    BUY_QTY           DECIMAL(18,4)     NOT NULL,
    BUY_PRICE         DECIMAL(18,4)     NOT NULL,
    BUY_AMOUNT        DECIMAL(18,4)     NOT NULL,
    BROKER_NAME       NVARCHAR(100)     NULL,
    CURRENCY_CODE     NVARCHAR(10)      NOT NULL CONSTRAINT DF_TB_PORTFOLIO_CURRENCY_CODE DEFAULT ('KRW'),
    REMARK            NVARCHAR(500)     NULL,
    USE_YN            CHAR(1)           NOT NULL CONSTRAINT DF_TB_PORTFOLIO_USE_YN DEFAULT ('Y'),
    DEL_YN            CHAR(1)           NOT NULL CONSTRAINT DF_TB_PORTFOLIO_DEL_YN DEFAULT ('N'),
    CREATED_AT        DATETIME2         NOT NULL CONSTRAINT DF_TB_PORTFOLIO_CREATED_AT DEFAULT (SYSDATETIME()),
    CREATED_BY        NVARCHAR(50)      NULL,
    UPDATED_AT        DATETIME2         NULL,
    UPDATED_BY        NVARCHAR(50)      NULL,
    CONSTRAINT PK_TB_PORTFOLIO PRIMARY KEY (PORTFOLIO_ID),
    CONSTRAINT CHK_TB_PORTFOLIO_BUY_QTY CHECK (BUY_QTY > 0),
    CONSTRAINT CHK_TB_PORTFOLIO_BUY_PRICE CHECK (BUY_PRICE > 0),
    CONSTRAINT CHK_TB_PORTFOLIO_BUY_AMOUNT CHECK (BUY_AMOUNT >= 0),
    CONSTRAINT CHK_TB_PORTFOLIO_USE_YN CHECK (USE_YN IN ('Y', 'N')),
    CONSTRAINT CHK_TB_PORTFOLIO_DEL_YN CHECK (DEL_YN IN ('Y', 'N'))
);


/* =========================================================
   3. 주가 이력 테이블 생성
   - 일자별 종목 시세
   ========================================================= */
CREATE TABLE dbo.TB_STOCK_PRICE
(
    PRICE_ID          INT IDENTITY(1,1) NOT NULL,
    PRICE_DATE        DATE              NOT NULL,
    TICKER            NVARCHAR(20)      NOT NULL,
    STOCK_NAME        NVARCHAR(100)     NOT NULL,
    OPEN_PRICE        DECIMAL(18,4)     NULL,
    HIGH_PRICE        DECIMAL(18,4)     NULL,
    LOW_PRICE         DECIMAL(18,4)     NULL,
    CLOSE_PRICE       DECIMAL(18,4)     NOT NULL,
    VOLUME            BIGINT            NULL,
    MARKET_TYPE       NVARCHAR(20)      NULL,
    CURRENCY_CODE     NVARCHAR(10)      NOT NULL CONSTRAINT DF_TB_STOCK_PRICE_CURRENCY_CODE DEFAULT ('KRW'),
    CREATED_AT        DATETIME2         NOT NULL CONSTRAINT DF_TB_STOCK_PRICE_CREATED_AT DEFAULT (SYSDATETIME()),
    CONSTRAINT PK_TB_STOCK_PRICE PRIMARY KEY (PRICE_ID),
    CONSTRAINT UQ_TB_STOCK_PRICE_01 UNIQUE (PRICE_DATE, TICKER),
    CONSTRAINT CHK_TB_STOCK_PRICE_CLOSE_PRICE CHECK (CLOSE_PRICE > 0),
    CONSTRAINT CHK_TB_STOCK_PRICE_OPEN_PRICE CHECK (OPEN_PRICE IS NULL OR OPEN_PRICE > 0),
    CONSTRAINT CHK_TB_STOCK_PRICE_HIGH_PRICE CHECK (HIGH_PRICE IS NULL OR HIGH_PRICE > 0),
    CONSTRAINT CHK_TB_STOCK_PRICE_LOW_PRICE CHECK (LOW_PRICE IS NULL OR LOW_PRICE > 0),
    CONSTRAINT CHK_TB_STOCK_PRICE_VOLUME CHECK (VOLUME IS NULL OR VOLUME >= 0)
);


/* =========================================================
   4. 인덱스 생성
   ========================================================= */
CREATE INDEX IX_TB_PORTFOLIO_01
    ON dbo.TB_PORTFOLIO (USER_ID, TICKER, BUY_DATE);

CREATE INDEX IX_TB_STOCK_PRICE_01
    ON dbo.TB_STOCK_PRICE (TICKER, PRICE_DATE);


/* =========================================================
   5. 샘플 데이터 입력 - 포트폴리오
   ========================================================= */
INSERT INTO dbo.TB_PORTFOLIO
(
    USER_ID,
    TICKER,
    STOCK_NAME,
    BUY_DATE,
    BUY_QTY,
    BUY_PRICE,
    BUY_AMOUNT,
    BROKER_NAME,
    CURRENCY_CODE,
    REMARK,
    CREATED_BY
)
VALUES
('admin', '005930', N'삼성전자',  '2026-03-10', 10.0000,  70000.0000,  700000.0000, N'키움증권', 'KRW', N'장기보유', 'admin'),
('admin', '000660', N'SK하이닉스', '2026-03-11',  5.0000, 210000.0000, 1050000.0000, N'키움증권', 'KRW', N'',         'admin'),
('admin', '005930', N'삼성전자',  '2026-03-20',  3.0000,  71000.0000,  213000.0000, N'키움증권', 'KRW', N'추가매수', 'admin');


/* =========================================================
   6. 샘플 데이터 입력 - 주가
   ========================================================= */
INSERT INTO dbo.TB_STOCK_PRICE
(
    PRICE_DATE,
    TICKER,
    STOCK_NAME,
    OPEN_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    CLOSE_PRICE,
    VOLUME,
    MARKET_TYPE,
    CURRENCY_CODE
)
VALUES
('2026-03-21', '005930', N'삼성전자',   70800.0000, 71500.0000, 70300.0000, 71200.0000, 12100000, 'KOSPI', 'KRW'),
('2026-03-22', '005930', N'삼성전자',   71200.0000, 71900.0000, 70900.0000, 71700.0000, 11800000, 'KOSPI', 'KRW'),
('2026-03-23', '005930', N'삼성전자',   71700.0000, 72000.0000, 71000.0000, 71500.0000, 12500000, 'KOSPI', 'KRW'),
('2026-03-21', '000660', N'SK하이닉스', 209000.0000, 213000.0000, 208500.0000, 211000.0000, 2800000, 'KOSPI', 'KRW'),
('2026-03-22', '000660', N'SK하이닉스', 211000.0000, 214500.0000, 210000.0000, 213500.0000, 3000000, 'KOSPI', 'KRW'),
('2026-03-23', '000660', N'SK하이닉스', 212000.0000, 215000.0000, 210500.0000, 214000.0000, 3200000, 'KOSPI', 'KRW');


/* =========================================================
   7. 데이터 확인
   ========================================================= */
SELECT *
FROM dbo.TB_PORTFOLIO
ORDER BY PORTFOLIO_ID;

SELECT *
FROM dbo.TB_STOCK_PRICE
ORDER BY TICKER, PRICE_DATE;


/* =========================================================
   8. 종목별 최신가 기준 포트폴리오 평가 조회
   - 매수건별 현황
   ========================================================= */
SELECT
    P.PORTFOLIO_ID,
    P.USER_ID,
    P.TICKER,
    P.STOCK_NAME,
    P.BUY_DATE,
    P.BUY_QTY,
    P.BUY_PRICE,
    P.BUY_AMOUNT,
    S.PRICE_DATE,
    S.CLOSE_PRICE AS CURRENT_PRICE,
    (P.BUY_QTY * S.CLOSE_PRICE) AS EVAL_AMOUNT,
    ((P.BUY_QTY * S.CLOSE_PRICE) - P.BUY_AMOUNT) AS PROFIT_LOSS,
    CASE
        WHEN P.BUY_AMOUNT = 0 THEN 0
        ELSE ROUND((((P.BUY_QTY * S.CLOSE_PRICE) - P.BUY_AMOUNT) / P.BUY_AMOUNT) * 100, 2)
    END AS RETURN_RATE
FROM dbo.TB_PORTFOLIO P
INNER JOIN dbo.TB_STOCK_PRICE S
    ON P.TICKER = S.TICKER
   AND S.PRICE_DATE = (
        SELECT MAX(S2.PRICE_DATE)
        FROM dbo.TB_STOCK_PRICE S2
        WHERE S2.TICKER = P.TICKER
   )
WHERE P.USER_ID = 'admin'
  AND P.USE_YN = 'Y'
  AND P.DEL_YN = 'N'
ORDER BY P.TICKER, P.BUY_DATE;
GO


/* =========================================================
   9. 종목별 집계 포트폴리오 현황
   - 같은 종목 추가매수까지 합산
   ========================================================= */
WITH LATEST_PRICE AS
(
    SELECT
        S.TICKER,
        S.STOCK_NAME,
        S.PRICE_DATE,
        S.CLOSE_PRICE,
        ROW_NUMBER() OVER (PARTITION BY S.TICKER ORDER BY S.PRICE_DATE DESC) AS RN
    FROM dbo.TB_STOCK_PRICE S
),
PORTFOLIO_SUM AS
(
    SELECT
        P.USER_ID,
        P.TICKER,
        MAX(P.STOCK_NAME) AS STOCK_NAME,
        SUM(P.BUY_QTY) AS TOTAL_BUY_QTY,
        SUM(P.BUY_AMOUNT) AS TOTAL_BUY_AMOUNT,
        CASE
            WHEN SUM(P.BUY_QTY) = 0 THEN 0
            ELSE ROUND(SUM(P.BUY_AMOUNT) / SUM(P.BUY_QTY), 4)
        END AS AVG_BUY_PRICE
    FROM dbo.TB_PORTFOLIO P
    WHERE P.USER_ID = 'admin'
      AND P.USE_YN = 'Y'
      AND P.DEL_YN = 'N'
    GROUP BY
        P.USER_ID,
        P.TICKER
)
SELECT
    A.USER_ID,
    A.TICKER,
    A.STOCK_NAME,
    A.TOTAL_BUY_QTY,
    A.AVG_BUY_PRICE,
    A.TOTAL_BUY_AMOUNT,
    L.PRICE_DATE,
    L.CLOSE_PRICE AS CURRENT_PRICE,
    ROUND(A.TOTAL_BUY_QTY * L.CLOSE_PRICE, 4) AS EVAL_AMOUNT,
    ROUND((A.TOTAL_BUY_QTY * L.CLOSE_PRICE) - A.TOTAL_BUY_AMOUNT, 4) AS PROFIT_LOSS,
    CASE
        WHEN A.TOTAL_BUY_AMOUNT = 0 THEN 0
        ELSE ROUND((((A.TOTAL_BUY_QTY * L.CLOSE_PRICE) - A.TOTAL_BUY_AMOUNT) / A.TOTAL_BUY_AMOUNT) * 100, 2)
    END AS RETURN_RATE
FROM PORTFOLIO_SUM A
INNER JOIN LATEST_PRICE L
    ON A.TICKER = L.TICKER
   AND L.RN = 1
ORDER BY A.TICKER;
GO


/* =========================================================
   10. 전체 포트폴리오 요약 KPI
   ========================================================= */
WITH LATEST_PRICE AS
(
    SELECT
        S.TICKER,
        S.CLOSE_PRICE,
        ROW_NUMBER() OVER (PARTITION BY S.TICKER ORDER BY S.PRICE_DATE DESC) AS RN
    FROM dbo.TB_STOCK_PRICE S
),
PORTFOLIO_SUM AS
(
    SELECT
        P.USER_ID,
        P.TICKER,
        SUM(P.BUY_QTY) AS TOTAL_BUY_QTY,
        SUM(P.BUY_AMOUNT) AS TOTAL_BUY_AMOUNT
    FROM dbo.TB_PORTFOLIO P
    WHERE P.USER_ID = 'admin'
      AND P.USE_YN = 'Y'
      AND P.DEL_YN = 'N'
    GROUP BY
        P.USER_ID,
        P.TICKER
)
SELECT
    SUM(A.TOTAL_BUY_AMOUNT) AS TOTAL_BUY_AMOUNT,
    SUM(A.TOTAL_BUY_QTY * L.CLOSE_PRICE) AS TOTAL_EVAL_AMOUNT,
    SUM((A.TOTAL_BUY_QTY * L.CLOSE_PRICE) - A.TOTAL_BUY_AMOUNT) AS TOTAL_PROFIT_LOSS,
    CASE
        WHEN SUM(A.TOTAL_BUY_AMOUNT) = 0 THEN 0
        ELSE ROUND(
            (SUM((A.TOTAL_BUY_QTY * L.CLOSE_PRICE) - A.TOTAL_BUY_AMOUNT) / SUM(A.TOTAL_BUY_AMOUNT)) * 100,
            2
        )
    END AS TOTAL_RETURN_RATE
FROM PORTFOLIO_SUM A
INNER JOIN LATEST_PRICE L
    ON A.TICKER = L.TICKER
   AND L.RN = 1;
GO
;




INSERT INTO dbo.TB_MENU (
    MENU_ID,
    MENU_CODE,
    MENU_NAME,
    PARENT_MENU_ID,
    MENU_LEVEL,
    SORT_NO,
    PAGE_KEY,
    MENU_TYPE,
    MENU_ICON,
    REMARK,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
VALUES
(70, 'INVEST_ANALYSIS',      N'투자/분석', 0, 1, 70, NULL,               'FOLDER', NULL, N'투자 분석 상위 메뉴', NULL, NULL, 'Y', 'N'),
(71, 'INVEST_MGMT',         N'투자관리',   70, 2, 1, 'invest_management', 'PAGE',   NULL, N'투자 등록/관리', NULL, NULL, 'Y', 'N'),
(72, 'INVEST_ANALYSIS_VIEW',N'투자분석',   70, 2, 2, 'invest_analysis',   'PAGE',   NULL, N'투자 분석 화면', NULL, NULL, 'Y', 'N'),
(73, 'INVEST_STATS',        N'투자통계',   70, 2, 3, 'invest_stats',      'PAGE',   NULL, N'통계/리포트', NULL, NULL, 'Y', 'N');


-- 예: ADMIN 권한
INSERT INTO dbo.TB_COMPANY_MENU (
    COMPANY_ID,
    MENU_ID,
    USE_YN,
    DEL_YN
)
VALUES
(1, 70, 'Y','N'),
(1, 71, 'Y','N'),
(1, 72, 'Y','N'),
(1, 73, 'Y','N');

SELECT * FROM TB_ROLE_MENU_PERMISSION

INSERT INTO DLAB.dbo.TB_ROLE_MENU_PERMISSION (
    COMPANY_ID,
    ROLE_ID,
    MENU_ID,
    READ_YN,
    WRITE_YN,
    DELETE_YN,
    EXCEL_YN,
    CREATED_BY,
    USE_YN,
    DEL_YN
)
VALUES
-- 투자/분석 (폴더)
(1, 1, 70, 'Y','Y','Y','Y', 1, 'Y','N'),
-- 투자관리
(1, 1, 71, 'Y','Y','Y','Y', 1, 'Y','N'),
-- 투자분석
(1, 1, 72, 'Y','Y','Y','Y', 1, 'Y','N'),
-- 투자통계
(1, 1, 73, 'Y','Y','Y','Y', 1, 'Y','N');



CREATE TABLE DLAB.dbo.TB_INVESTMENT (
    INVEST_ID int IDENTITY(1,1) NOT NULL,
    INVEST_CODE varchar(30) NOT NULL,
    INVEST_NAME nvarchar(100) NOT NULL,
    INVEST_TYPE varchar(30) NOT NULL,
    INVEST_AMOUNT decimal(18,2) NOT NULL DEFAULT 0,
    INVEST_DATE date NOT NULL,
    REMARK nvarchar(500) NULL,
    USE_YN char(1) NOT NULL DEFAULT 'Y',
    DEL_YN char(1) NOT NULL DEFAULT 'N',
    CREATED_AT datetime NOT NULL DEFAULT GETDATE(),
    CREATED_BY int NULL,
    UPDATED_AT datetime NULL,
    UPDATED_BY int NULL,
    CONSTRAINT PK_TB_INVESTMENT PRIMARY KEY (INVEST_ID)
);


INSERT INTO DLAB.dbo.TB_INVESTMENT
(
    INVEST_CODE,
    INVEST_NAME,
    INVEST_TYPE,
    INVEST_AMOUNT,
    INVEST_DATE,
    REMARK,
    CREATED_BY
)
VALUES
('INV-001', 'Samsung Electronics', 'Stock', 1000000, '2026-03-01', 'Long term holding', 1),
('INV-002', 'KODEX 200', 'ETF', 500000, '2026-03-05', 'Index tracking ETF', 1),
('INV-003', 'USD Deposit', 'Cash', 300000, '2026-03-10', 'Foreign currency position', 1);


ALTER TABLE DLAB.dbo.TB_INVESTMENT
ADD TICKER_SYMBOL varchar(20);
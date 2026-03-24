SET NOCOUNT ON;
GO

DECLARE @NOW_USER_ID INT = NULL;
DECLARE @COMPANY_ID INT;
DECLARE @ADMIN_USER_ID INT;
DECLARE @ADMIN_ROLE_ID INT;

--------------------------------------------------
-- 1. 업체
--------------------------------------------------
INSERT INTO dbo.TB_COMPANY (
    COMPANY_CODE,
    COMPANY_NAME,
    BUSINESS_NO,
    CEO_NAME,
    TEL_NO,
    ADDRESS,
    SERVICE_START_DATE,
    SERVICE_END_DATE,
    REMARK,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
VALUES (
    'ONTIDE',
    N'ONTIDE',
    '123-45-67890',
    N'John Smith',
    '02-1234-5678',
    N'Seoul, Korea',
    CAST(GETDATE() AS DATE),
    DATEADD(YEAR, 1, CAST(GETDATE() AS DATE)),
    N'초기 샘플 업체',
    NULL,
    NULL,
    'Y',
    'N'
);

SELECT @COMPANY_ID = SCOPE_IDENTITY();

--------------------------------------------------
-- 2. 사용자
--------------------------------------------------
INSERT INTO dbo.TB_USER (
    COMPANY_ID,
    LOGIN_ID,
    USER_NAME,
    PASSWORD,
    EMAIL,
    MOBILE_NO,
    LAST_LOGIN_AT,
    PASSWORD_CHANGED_AT,
    REMARK,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
VALUES (
    @COMPANY_ID,
    'ADMIN',
    N'System Admin',
    'admin123',
    'admin@ontide.local',
    '010-0000-0000',
    NULL,
    NULL,
    N'초기 관리자 계정',
    NULL,
    NULL,
    'Y',
    'N'
);

SELECT @ADMIN_USER_ID = SCOPE_IDENTITY();

--------------------------------------------------
-- 3. 권한
--------------------------------------------------
INSERT INTO dbo.TB_ROLE (
    COMPANY_ID,
    ROLE_CODE,
    ROLE_NAME,
    REMARK,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
VALUES (
    @COMPANY_ID,
    'ADMIN',
    N'System Administrator',
    N'전체 권한',
    NULL,
    NULL,
    'Y',
    'N'
);

SELECT @ADMIN_ROLE_ID = SCOPE_IDENTITY();

--------------------------------------------------
-- 4. 사용자-권한 연결
--------------------------------------------------
INSERT INTO dbo.TB_USER_ROLE (
    COMPANY_ID,
    USER_ID,
    ROLE_ID,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
VALUES (
    @COMPANY_ID,
    @ADMIN_USER_ID,
    @ADMIN_ROLE_ID,
    NULL,
    NULL,
    'Y',
    'N'
);

--------------------------------------------------
-- 5. 메뉴 마스터
--------------------------------------------------
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
(1,   'DASHBOARD',         N'Dashboard',           0, 1,  1, 'dashboard',            'PAGE',   NULL, N'기본 대시보드', NULL, NULL, 'Y', 'N'),
(10,  'MASTER_DATA',       N'Master Data',         0, 1, 10, NULL,                   'FOLDER', NULL, N'기준정보 폴더', NULL, NULL, 'Y', 'N'),
(11,  'CUSTOMER_MGMT',     N'Customer Management', 10, 2,  1, 'customer_management', 'PAGE',   NULL, N'거래처관리',     NULL, NULL, 'Y', 'N'),
(12,  'ITEM_MGMT',         N'Item Management',     10, 2,  2, 'item_management',     'PAGE',   NULL, N'품목관리',       NULL, NULL, 'Y', 'N'),
(20,  'PURCHASING',        N'Purchasing',          0, 1, 20, NULL,                   'FOLDER', NULL, N'구매관리 폴더', NULL, NULL, 'Y', 'N'),
(21,  'PURCHASE_ORDER',    N'Purchase Orders',     20, 2,  1, 'purchase_order',      'PAGE',   NULL, N'발주관리',       NULL, NULL, 'Y', 'N'),
(22,  'PURCHASE_RECEIPT',  N'Purchase Receipts',   20, 2,  2, 'purchase_receipt',    'PAGE',   NULL, N'입고관리',       NULL, NULL, 'Y', 'N'),
(90,  'SYSTEM_ADMIN',      N'System Administration', 0, 1, 90, NULL,                 'FOLDER', NULL, N'시스템관리 폴더', NULL, NULL, 'Y', 'N'),
(91,  'USER_MGMT',         N'User Management',     90, 2,  1, 'user_management',     'PAGE',   NULL, N'사용자관리',     NULL, NULL, 'Y', 'N'),
(92,  'ROLE_MGMT',         N'Role Management',     90, 2,  2, 'role_management',     'PAGE',   NULL, N'권한관리',       NULL, NULL, 'Y', 'N'),
(93,  'MENU_MGMT',         N'Menu Management',     90, 2,  3, 'menu_management',     'PAGE',   NULL, N'메뉴관리',       NULL, NULL, 'Y', 'N');

--------------------------------------------------
-- 6. 업체별 메뉴 사용 설정
--------------------------------------------------
INSERT INTO dbo.TB_COMPANY_MENU (
    COMPANY_ID,
    MENU_ID,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
SELECT
    @COMPANY_ID,
    M.MENU_ID,
    NULL,
    NULL,
    'Y',
    'N'
FROM dbo.TB_MENU M
WHERE M.DEL_YN = 'N';

--------------------------------------------------
-- 7. 권한별 메뉴 권한
--------------------------------------------------
INSERT INTO dbo.TB_ROLE_MENU_PERMISSION (
    COMPANY_ID,
    ROLE_ID,
    MENU_ID,
    READ_YN,
    WRITE_YN,
    DELETE_YN,
    EXCEL_YN,
    CREATED_BY,
    UPDATED_BY,
    USE_YN,
    DEL_YN
)
SELECT
    @COMPANY_ID,
    @ADMIN_ROLE_ID,
    M.MENU_ID,
    'Y',
    'Y',
    'Y',
    'Y',
    NULL,
    NULL,
    'Y',
    'N'
FROM dbo.TB_MENU M
WHERE M.DEL_YN = 'N';

PRINT 'Initial seed data completed.';
GO
CHAT_URL = "https://www.douyin.com/im"

# Ordered alternatives keep page-specific changes isolated from the workflow.
LOGIN_MARKERS = (
    'input[placeholder*="搜索"]',
    '[role="textbox"][placeholder*="搜索"]',
    'text=私信',
)
LOGIN_REQUIRED_MARKERS = (
    'text=扫码登录',
    'text=验证码登录',
    'text=登录后',
)
RISK_MARKERS = (
    'text=安全验证',
    'text=完成验证',
    'text=验证身份',
)
SEARCH_INPUTS = (
    'input[placeholder*="搜索"]',
    '[role="textbox"][placeholder*="搜索"]',
)
MESSAGE_INPUTS = (
    '[contenteditable="true"][data-placeholder*="发送消息"]',
    '[contenteditable="true"][aria-label*="消息"]',
    '[contenteditable="true"]',
    'textarea[placeholder*="消息"]',
)
IMAGE_INPUTS = ('input[type="file"][accept*="image"]', 'input[type="file"]')
STICKER_BUTTONS = (
    'button[aria-label*="表情"]',
    '[role="button"][aria-label*="表情"]',
    '[title*="表情"]',
)
STICKER_PANELS = ('[role="dialog"]', '[class*="emoji"]', '[class*="sticker"]')

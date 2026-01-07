# location: finance/constants.py
# Default categories for new users
DEFAULT_CATEGORIES = {
    "income": [
        ("Salary", "💼", "#4CAF50"),
        ("Business", "🏢", "#2196F3"),
        ("Gift", "🎁", "#FF9800"),
        ("Investment", "📈", "#9C27B0"),
        ("Other Income", "💵", "#00BCD4")
    ],
    "expense": [
        ("Food", "🍔", "#FF5722"),
        ("Transport", "🚌", "#795548"),
        ("Shopping", "🛍️", "#E91E63"),
        ("Bills", "💡", "#FFC107"),
        ("Entertainment", "🎬", "#3F51B5")
    ]
}

# Default accounts for new users
DEFAULT_ACCOUNTS = [
    ("Bank", "🏦", 0.0),
    ("Card", "💳", 0.0),
    ("Cash", "💰", 0.0),
    ("Saving", "🐖", 0.0)
]

# Default account icons for dropdowns
DEFAULT_ACCOUNT_ICONS = [
    ("🏦", "Bank"), ("💳", "Card"), ("💰", "Cash"), ("🐖", "Saving"),
    ("💸", "Wallet"), ("🏠", "Home"), ("🛒", "Shopping"), ("🚗", "Car"),
    ("🎓", "Education"), ("💼", "Work"),
    ("🍔", "Food"), ("☕", "Coffee"), ("🎁", "Gifts"), ("🏖️", "Travel"),
    ("🎮", "Games"), ("📚", "Books"), ("🏥", "Health"), ("🛏️", "Rent"),
    ("⚽", "Sports"), ("🎵", "Music")
]

# Default category icons for modal selection
DEFAULT_CATEGORY_ICONS = [
    ("🍔", "Food"), ("🚌", "Transport"), ("🛍️", "Shopping"),
    ("💡", "Bills"), ("🎬", "Entertainment"), ("💼", "Work"),
    ("🎁", "Gift"), ("💊", "Health"), ("📚", "Education"),
    ("☕", "Coffee"), ("🏠", "Home"), ("🚗", "Transport"),
    ("💵", "Other Income"), ("📈", "Investment"), ("🎮", "Games"),
    ("🏖️", "Travel"), ("⚡", "Utilities"), ("🎉", "Party"),
]

# New: default category colors
DEFAULT_CATEGORY_COLORS = [
    "#FF5722", "#795548", "#E91E63", "#FFC107", "#3F51B5", "#4CAF50", "#2196F3",
    "#9C27B0", "#00BCD4", "#FF9800", "#607D8B", "#009688", "#8BC34A", "#CDDC39",
    "#FFEB3B", "#FFCDD2", "#F8BBD0", "#E1BEE7", "#D1C4E9", "#BBDEFB", "#B2DFDB",
    "#C8E6C9", "#DCEDC8", "#F0F4C3", "#FFE0B2", "#FFCCBC", "#D7CCC8"
]

// Основная функциональность браузера nokssss
document.addEventListener('DOMContentLoaded', function() {
    initializeBrowser();
});

function initializeBrowser() {
    setupTabFunctionality();
    setupNavigationButtons();
    setupAddressBar();
    setupSearchFunctionality();
    setupShortcuts();
    setupWindowControls();
    setupZoomControls();
    addGlowEffects();
}

// Функциональность вкладок
function setupTabFunctionality() {
    const tabs = document.querySelectorAll('.tab');
    const newTabBtn = document.querySelector('.new-tab-btn');
    const tabsContainer = document.querySelector('.tabs-container');

    // Переключение между вкладками
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            if (e.target.classList.contains('tab-close')) {
                return; // Не переключаем вкладку при клике на закрытие
            }
            
            // Убираем активный класс со всех вкладок
            tabs.forEach(t => t.classList.remove('active'));
            // Добавляем активный класс к кликнутой вкладке
            this.classList.add('active');
            
            // Анимация переключения
            animateTabSwitch(this);
        });
    });

    // Закрытие вкладок
    document.querySelectorAll('.tab-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const tab = this.closest('.tab');
            closeTab(tab);
        });
    });

    // Создание новой вкладки
    newTabBtn.addEventListener('click', function() {
        createNewTab();
    });
}

function animateTabSwitch(activeTab) {
    activeTab.style.transform = 'scale(1.05)';
    setTimeout(() => {
        activeTab.style.transform = 'scale(1)';
    }, 150);
}

function closeTab(tab) {
    tab.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => {
        tab.remove();
        // Если закрыли активную вкладку, активируем первую доступную
        if (!document.querySelector('.tab.active')) {
            const firstTab = document.querySelector('.tab');
            if (firstTab) {
                firstTab.classList.add('active');
            }
        }
    }, 300);
}

function createNewTab() {
    const tabsContainer = document.querySelector('.tabs-container');
    const newTab = document.createElement('div');
    newTab.className = 'tab active';
    newTab.innerHTML = `
        <span class="tab-icon">🌐</span>
        <span class="tab-title">Новая вкладка</span>
        <button class="tab-close">×</button>
    `;

    // Убираем активный класс с других вкладок
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    tabsContainer.appendChild(newTab);
    
    // Добавляем обработчики для новой вкладки
    setupNewTabHandlers(newTab);
    
    // Анимация появления
    newTab.style.opacity = '0';
    newTab.style.transform = 'translateX(20px)';
    setTimeout(() => {
        newTab.style.transition = 'all 0.3s ease';
        newTab.style.opacity = '1';
        newTab.style.transform = 'translateX(0)';
    }, 50);
}

function setupNewTabHandlers(tab) {
    tab.addEventListener('click', function(e) {
        if (e.target.classList.contains('tab-close')) {
            return;
        }
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        animateTabSwitch(this);
    });

    const closeBtn = tab.querySelector('.tab-close');
    closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        closeTab(tab);
    });
}

// Навигационные кнопки
function setupNavigationButtons() {
    const backBtn = document.querySelector('.nav-btn.back');
    const forwardBtn = document.querySelector('.nav-btn.forward');
    const refreshBtn = document.querySelector('.nav-btn.refresh');
    const homeBtn = document.querySelector('.nav-btn.home');

    let navigationHistory = ['https://nokssss.com'];
    let currentIndex = 0;

    backBtn.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            navigateToUrl(navigationHistory[currentIndex]);
            updateNavigationButtons();
        }
        addClickEffect(this);
    });

    forwardBtn.addEventListener('click', function() {
        if (currentIndex < navigationHistory.length - 1) {
            currentIndex++;
            navigateToUrl(navigationHistory[currentIndex]);
            updateNavigationButtons();
        }
        addClickEffect(this);
    });

    refreshBtn.addEventListener('click', function() {
        refreshPage();
        addClickEffect(this);
    });

    homeBtn.addEventListener('click', function() {
        const homeUrl = 'https://nokssss.com';
        navigateToUrl(homeUrl);
        if (navigationHistory[currentIndex] !== homeUrl) {
            navigationHistory = navigationHistory.slice(0, currentIndex + 1);
            navigationHistory.push(homeUrl);
            currentIndex++;
        }
        updateNavigationButtons();
        addClickEffect(this);
    });

    function updateNavigationButtons() {
        backBtn.disabled = currentIndex === 0;
        forwardBtn.disabled = currentIndex === navigationHistory.length - 1;
    }

    function navigateToUrl(url) {
        const addressBar = document.querySelector('.address-bar');
        addressBar.value = url;
        updatePageContent(url);
    }

    function refreshPage() {
        const refreshIcon = refreshBtn.textContent;
        refreshBtn.textContent = '↻';
        refreshBtn.style.animation = 'spin 1s linear';
        
        setTimeout(() => {
            refreshBtn.textContent = refreshIcon;
            refreshBtn.style.animation = '';
            showNotification('Страница обновлена');
        }, 1000);
    }

    // Инициализация состояния кнопок
    updateNavigationButtons();
}

// Адресная строка
function setupAddressBar() {
    const addressBar = document.querySelector('.address-bar');
    const bookmarkBtn = document.querySelector('.bookmark-btn');

    addressBar.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const url = this.value.trim();
            if (url) {
                navigateToAddress(url);
            }
        }
    });

    addressBar.addEventListener('focus', function() {
        this.select();
        addGlowEffect(this.parentElement);
    });

    addressBar.addEventListener('blur', function() {
        removeGlowEffect(this.parentElement);
    });

    bookmarkBtn.addEventListener('click', function() {
        toggleBookmark();
        addClickEffect(this);
    });

    function navigateToAddress(url) {
        // Простая валидация URL
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            if (url.includes('.')) {
                url = 'https://' + url;
            } else {
                url = 'https://www.google.com/search?q=' + encodeURIComponent(url);
            }
        }
        
        addressBar.value = url;
        updatePageContent(url);
        showNotification(`Переход на ${url}`);
    }

    function toggleBookmark() {
        const isBookmarked = bookmarkBtn.classList.contains('bookmarked');
        if (isBookmarked) {
            bookmarkBtn.classList.remove('bookmarked');
            bookmarkBtn.textContent = '⭐';
            showNotification('Закладка удалена');
        } else {
            bookmarkBtn.classList.add('bookmarked');
            bookmarkBtn.textContent = '★';
            showNotification('Страница добавлена в закладки');
        }
    }
}

// Поисковая функциональность
function setupSearchFunctionality() {
    const mainSearch = document.querySelector('.main-search');
    const searchBtn = document.querySelector('.search-btn');

    function performSearch() {
        const query = mainSearch.value.trim();
        if (query) {
            const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
            document.querySelector('.address-bar').value = searchUrl;
            updatePageContent(searchUrl);
            showNotification(`Поиск: ${query}`);
        }
    }

    searchBtn.addEventListener('click', performSearch);
    
    mainSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    mainSearch.addEventListener('focus', function() {
        addGlowEffect(this);
    });

    mainSearch.addEventListener('blur', function() {
        removeGlowEffect(this);
    });
}

// Быстрые ссылки
function setupShortcuts() {
    const shortcuts = document.querySelectorAll('.shortcut-card');
    
    const shortcutUrls = {
        'Google': 'https://www.google.com',
        'YouTube': 'https://www.youtube.com',
        'GitHub': 'https://github.com',
        'Reddit': 'https://www.reddit.com',
        'Amazon': 'https://www.amazon.com',
        'Gmail': 'https://mail.google.com'
    };

    shortcuts.forEach(shortcut => {
        shortcut.addEventListener('click', function() {
            const siteName = this.querySelector('span').textContent;
            const url = shortcutUrls[siteName];
            if (url) {
                document.querySelector('.address-bar').value = url;
                updatePageContent(url);
                showNotification(`Переход на ${siteName}`);
            }
            addClickEffect(this);
        });

        // Эффект при наведении
        shortcut.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.05)';
        });

        shortcut.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Управление окном
function setupWindowControls() {
    const minimizeBtn = document.querySelector('.control-btn.minimize');
    const maximizeBtn = document.querySelector('.control-btn.maximize');
    const closeBtn = document.querySelector('.control-btn.close');

    minimizeBtn.addEventListener('click', function() {
        showNotification('Окно свернуто');
        addClickEffect(this);
    });

    maximizeBtn.addEventListener('click', function() {
        const browserWindow = document.querySelector('.browser-window');
        if (browserWindow.classList.contains('maximized')) {
            browserWindow.classList.remove('maximized');
            showNotification('Окно восстановлено');
        } else {
            browserWindow.classList.add('maximized');
            showNotification('Окно развернуто');
        }
        addClickEffect(this);
    });

    closeBtn.addEventListener('click', function() {
        if (confirm('Закрыть браузер nokssss?')) {
            document.body.style.animation = 'fadeOut 0.5s ease-out';
            setTimeout(() => {
                document.body.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100vh; color: #00ff41; font-size: 24px; text-shadow: 0 0 10px currentColor;">Браузер nokssss закрыт</div>';
            }, 500);
        }
        addClickEffect(this);
    });
}

// Управление масштабом
function setupZoomControls() {
    const zoomInBtn = document.querySelector('.zoom-btn:last-child');
    const zoomOutBtn = document.querySelector('.zoom-btn:first-child');
    const zoomLevel = document.querySelector('.zoom-level');
    
    let currentZoom = 100;

    zoomInBtn.addEventListener('click', function() {
        if (currentZoom < 200) {
            currentZoom += 10;
            updateZoom();
        }
        addClickEffect(this);
    });

    zoomOutBtn.addEventListener('click', function() {
        if (currentZoom > 50) {
            currentZoom -= 10;
            updateZoom();
        }
        addClickEffect(this);
    });

    function updateZoom() {
        zoomLevel.textContent = currentZoom + '%';
        document.querySelector('.content-area').style.transform = `scale(${currentZoom / 100})`;
        document.querySelector('.content-area').style.transformOrigin = 'top center';
        showNotification(`Масштаб: ${currentZoom}%`);
    }
}

// Вспомогательные функции
function updatePageContent(url) {
    // Симуляция загрузки страницы
    const contentArea = document.querySelector('.content-area');
    contentArea.style.opacity = '0.5';
    
    setTimeout(() => {
        contentArea.style.opacity = '1';
        // Обновляем заголовок активной вкладки
        const activeTab = document.querySelector('.tab.active .tab-title');
        if (activeTab) {
            const domain = extractDomain(url);
            activeTab.textContent = domain || 'nokssss';
        }
    }, 500);
}

function extractDomain(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname;
    } catch {
        return url.split('/')[0];
    }
}

function showNotification(message) {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-secondary);
        color: var(--neon-green);
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid var(--neon-green);
        box-shadow: var(--shadow-neon);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        font-size: 14px;
        text-shadow: 0 0 5px currentColor;
    `;

    document.body.appendChild(notification);

    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function addClickEffect(element) {
    element.style.transform = 'scale(0.95)';
    setTimeout(() => {
        element.style.transform = '';
    }, 150);
}

function addGlowEffect(element) {
    element.style.boxShadow = 'var(--shadow-neon-strong)';
}

function removeGlowEffect(element) {
    element.style.boxShadow = '';
}

function addGlowEffects() {
    // Добавляем случайные эффекты свечения к элементам
    const glowElements = document.querySelectorAll('.nav-btn, .control-btn, .tab');
    
    glowElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.textShadow = 'var(--shadow-neon)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.textShadow = '0 0 5px currentColor';
        });
    });
}

// Добавляем дополнительные анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    
    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    
    .browser-window.maximized {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
    }
    
    .bookmarked {
        color: var(--neon-green) !important;
        text-shadow: var(--shadow-neon) !important;
    }
`;

document.head.appendChild(style);

// Пасхальное яйцо: команды в адресной строке
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'K') {
        e.preventDefault();
        showEasterEgg();
    }
});

function showEasterEgg() {
    const message = `
    ╔══════════════════════════════════════╗
    ║            nokssss v1.0.0            ║
    ║                                      ║
    ║   Создан с использованием технологий ║
    ║            будущего 🚀               ║
    ║                                      ║
    ║     Неоновые мечты в темной сети     ║
    ╚══════════════════════════════════════╝
    `;
    
    const easterEgg = document.createElement('div');
    easterEgg.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-primary);
        color: var(--neon-green);
        padding: 30px;
        border: 2px solid var(--neon-green);
        border-radius: 12px;
        font-family: monospace;
        font-size: 12px;
        white-space: pre;
        z-index: 9999;
        box-shadow: var(--shadow-neon-strong);
        text-shadow: 0 0 5px currentColor;
        animation: glow 1s ease-in-out infinite alternate;
    `;
    
    easterEgg.textContent = message;
    document.body.appendChild(easterEgg);
    
    setTimeout(() => {
        easterEgg.remove();
    }, 5000);
}
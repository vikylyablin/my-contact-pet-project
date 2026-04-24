/**
 * CONTACTBOOK JS CORE
 * Управление контактами, сортировка и работа с API
 */

const BASE_URL = 'http://localhost:8000/contacts/';
let contactsCache = [];
let currentContact = null;
let currentFilter = 'all';
let isDarkMode = localStorage.getItem('darkMode') === 'true';

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        updateThemeToggleIcon();
    }
    loadContacts();
    setupEventListeners();
});

// Открыть модальное окно добавления контакта
function openAddModal() {
    const form = document.getElementById('addForm');
    form.reset();
    const preview = document.getElementById('avatarAddPreview');
    preview.src = '';
    preview.style.display = 'none';
    document.getElementById('addAvatar').value = '';
    document.getElementById('addModal').style.display = 'flex';
}

// 1. ЗАГРУЗКА СПИСКА (GET)
async function loadContacts() {
    try {
        const response = await fetch(BASE_URL);
        if (!response.ok) throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
        
        contactsCache = await response.json();
        renderContacts(contactsCache);
    } catch (err) {
        const list = document.getElementById('contact-list');
        if (list) {
            list.innerHTML = '<p class="empty-state">Нет соединения с сервером.</p>';
        }
        showToast(err.message || "Ошибка связи с сервером", "danger");
    }
}

// 2. ОТРИСОВКА СПИСКА С ГРУППИРОВКОЙ
function renderContacts(data) {
    const list = document.getElementById('contact-list');
    list.innerHTML = '';

    data.sort((a, b) => {
        if (a.is_pinned !== b.is_pinned) {
            return a.is_pinned ? -1 : 1;
        }
        return a.name.localeCompare(b.name);
    });

    const pinnedContacts = data.filter((c) => c.is_pinned);
    const normalContacts = data.filter((c) => !c.is_pinned);

    if (pinnedContacts.length) {
        const section = document.createElement('div');
        section.className = 'letter-divider';
        section.innerText = 'Закреплено';
        list.appendChild(section);
        pinnedContacts.forEach(contact => list.appendChild(createContactCard(contact)));
    }

    let lastLetter = '';
    normalContacts.forEach(contact => {
        const currentLetter = contact.name[0].toUpperCase();
        if (currentLetter !== lastLetter) {
            const divider = document.createElement('div');
            divider.className = 'letter-divider';
            divider.innerText = currentLetter;
            list.appendChild(divider);
            lastLetter = currentLetter;
        }
        list.appendChild(createContactCard(contact));
    });
}

function createContactCard(contact) {
    const card = document.createElement('div');
    card.className = 'contact-card-small';

    const avatarContent = contact.avatar
        ? `<img src="${contact.avatar}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">`
        : `<div class="mini-avatar">${contact.name[0].toUpperCase()}</div>`;

    const avatarWrapper = document.createElement('div');
    avatarWrapper.className = 'avatar-wrapper';
    avatarWrapper.innerHTML = avatarContent;

    const info = document.createElement('div');
    info.className = 'card-info';
    info.innerHTML = `<strong>${contact.name}</strong>`;

    const pinButton = document.createElement('button');
    pinButton.type = 'button';
    pinButton.className = `contact-pin ${contact.is_pinned ? 'pinned' : ''}`;
    pinButton.innerHTML = `<i class="${contact.is_pinned ? 'fas' : 'far'} fa-star"></i>`;
    pinButton.title = contact.is_pinned ? 'Открепить' : 'Закрепить';
    pinButton.addEventListener('click', (event) => {
        event.stopPropagation();
        togglePinnedContact(contact.id, contact.is_pinned);
    });

    card.appendChild(avatarWrapper);
    card.appendChild(info);
    card.appendChild(pinButton);

    card.addEventListener('click', () => showContactDetails(contact));

    return card;
}


// 3. ОТОБРАЖЕНИЕ ДЕТАЛЕЙ СПРАВА
function showContactDetails(contact) {
    currentContact = contact;
    const display = document.getElementById('contact-details');
    const firstLetter = contact.name[0].toUpperCase();
    const avatarSrc = contact.avatar ? `<img src="${contact.avatar}" style="width: 100%; height: 100%; object-fit: cover;">` : firstLetter;

    display.innerHTML = `
        <div class="profile-main-card">
            <div class="avatar-huge">${avatarSrc}</div>
            <h2 class="profile-name" style="margin-bottom: 5px; font-size: 24px;">${contact.name}</h2>
            <p class="profile-phone" style="color: #888; font-size: 14px;">${contact.phone}</p>

            <div class="action-row">
                <button class="btn-round call"><i class="fas fa-phone"></i></button>
                <button class="btn-round chat"><i class="fas fa-comment"></i></button>
                <button class="btn-round mail"><i class="fas fa-envelope"></i></button>
            </div>

            <div class="info-tiles">
                <div class="tile">
                    <label>Телефон</label>
                    <p>${contact.phone}</p>
                </div>
                <div class="tile">
                    <label>Email</label>
                    <p>${contact.email || '—'}</p>
                </div>
                <div class="tile">
                    <label>Адрес</label>
                    <p>${contact.address || '—'}</p>
                </div>
                <div class="tile">
                    <label>Категория</label>
                    <p>${contact.category || '—'}</p>
                </div>
                <div class="tile full-width">
                    <label>Заметка</label>
                    <p>${contact.note || 'Нет дополнительных записей'}</p>
                </div>
            </div>

            <div class="admin-actions">
                <button class="btn-secondary ${contact.is_pinned ? 'pinned' : ''}" onclick="togglePinnedContact(${contact.id}, ${contact.is_pinned})">
                    <i class="fa${contact.is_pinned ? 's' : 'r'} fa-star"></i> ${contact.is_pinned ? 'Открепить' : 'Закрепить'}
                </button>
                <button class="btn-primary" onclick="openEditMode()">
                    <i class="fas fa-edit"></i> Редактировать
                </button>
                <button class="btn-danger" onclick="deleteContactProcess(${contact.id}, '${contact.name}')">
                    <i class="fas fa-trash-alt"></i> Удалить
                </button>
            </div>
        </div>
    `;
}

// 4. СОЗДАНИЕ (POST)
document.getElementById('addForm').onsubmit = async (e) => {
    e.preventDefault();
    let avatar = null;
    const avatarFile = document.getElementById('addAvatar').files[0];
    if (avatarFile) {
        avatar = await fileToBase64(avatarFile);
    }
    const payload = {
        name: document.getElementById('addName').value,
        phone: document.getElementById('addPhone').value,
        email: document.getElementById('addEmail').value,
        category: document.getElementById('addCategory').value,
        address: document.getElementById('addAddress').value,
        note: document.getElementById('addNote').value
    };
    if (avatar) {
        payload.avatar = avatar;
    }

    try {
        const res = await fetch(BASE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            showToast("Контакт создан!");
            const preview = document.getElementById('avatarAddPreview');
            preview.src = '';
            preview.style.display = 'none';
            e.target.reset();
            closeModal('addModal');
            loadContacts();
        } else {
            const errorText = await res.text();
            showToast(errorText || "Ошибка при создании", "danger");
        }
    } catch (err) {
        showToast(err.message || "Ошибка при создании", "danger");
    }
};

// 5. УДАЛЕНИЕ (DELETE) - Используем эндпоинт по id
async function deleteContactProcess(contactId, contactName) {
    if (!confirm(`Удалить контакт ${contactName}?`)) return;

    try {
        const res = await fetch(`${BASE_URL}${contactId}/`, {
            method: 'DELETE'
        });

        if (res.ok) {
            showToast("Контакт удален");
            document.getElementById('contact-details').innerHTML = '';
            loadContacts();
        } else {
            const errorText = await res.text();
            showToast(errorText || "Ошибка при удалении", "danger");
        }
    } catch (err) {
        showToast(err.message || "Не удалось удалить", "danger");
    }
}

async function togglePinnedContact(contactId, currentPinned) {
    if (contactId === undefined || contactId === null) return;
        const res = await fetch(`${BASE_URL}${contactId}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_pinned: !currentPinned })
        });

    if (res.ok) {
        const updatedContact = await res.json();
        showToast(updatedContact.is_pinned ? 'Контакт закреплен' : 'Контакт откреплен');
        currentContact = updatedContact;
        showContactDetails(updatedContact);
        loadContacts();
    } else {
        showToast('Не удалось изменить закрепление', 'danger');
    }
}

// 6. ОБНОВЛЕНИЕ (PATCH)
async function openEditMode() {
    if (!currentContact) return;
    document.getElementById('editId').value = currentContact.id;
    document.getElementById('editName').value = currentContact.name;
    document.getElementById('editPhone').value = currentContact.phone;
    document.getElementById('editEmail').value = currentContact.email || '';
    document.getElementById('editCategory').value = currentContact.category || '';
    document.getElementById('editAddress').value = currentContact.address || '';
    document.getElementById('editNote').value = currentContact.note || '';
    if (currentContact.avatar) {
        const preview = document.getElementById('avatarPreview');
        preview.src = currentContact.avatar;
        preview.style.display = 'block';
    } else {
        document.getElementById('avatarPreview').style.display = 'none';
    }
    openModal('editModal');
}

const editFormElement = document.getElementById('editForm');
if (editFormElement) {
    editFormElement.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('editId').value;
        const avatarFile = document.getElementById('editAvatar').files[0];
        let avatar = undefined;
        if (avatarFile) {
            avatar = await fileToBase64(avatarFile);
        }
        const data = {
            name: document.getElementById('editName').value,
            phone: document.getElementById('editPhone').value,
            email: document.getElementById('editEmail').value,
            category: document.getElementById('editCategory').value,
            address: document.getElementById('editAddress').value,
            note: document.getElementById('editNote').value
        };
        if (avatar !== undefined) {
            data.avatar = avatar;
        }

        const res = await fetch(`${BASE_URL}${id}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            const updatedContact = await res.json();
            showToast("Обновлено!");
            closeModal('editModal');
            currentContact = updatedContact;
            showContactDetails(updatedContact);
            loadContacts();
        } else {
            showToast("Ошибка обновления", "danger");
        }
    };
}

// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (Модалки, Поиск, Тосты, Аватар)
function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function previewAvatar(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewId = event.target.id === 'addAvatar' ? 'avatarAddPreview' : 'avatarPreview';
            const preview = document.getElementById(previewId);
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

function setupEventListeners() {
    // Поиск
    document.getElementById('searchInput').oninput = (e) => {
        const val = e.target.value.toLowerCase();
        const filtered = contactsCache.filter(c => c.name.toLowerCase().includes(val));
        applyFilter(filtered);
    };

    // Фильтры по категориям
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            applyFilter(contactsCache);
        });
    });

    // Переключение темы
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleDarkMode);
    }
}

function applyFilter(data) {
    let filtered = data;
    
    if (currentFilter === 'pinned') {
        filtered = data.filter(c => c.is_pinned);
    } else if (currentFilter !== 'all') {
        filtered = data.filter(c => c.category === currentFilter);
    }
    
    renderContacts(filtered);
}

function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('darkMode', isDarkMode);
    document.body.classList.toggle('dark-mode');
    updateThemeToggleIcon();
}

function updateThemeToggleIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
}

function showToast(msg, type = "success") {
    const container = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerText = msg;
    container.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}
// Объем кода JavaScript увеличен за счет полной реализации CRUD, фильтрации и UI-утилит
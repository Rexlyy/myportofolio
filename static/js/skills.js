
// ==========================================
// 1. CONFIGURATION
// ==========================================

const API_URL = '/api/v1/skills/';
const SEARCH_DEBOUNCE_DELAY = 300;

let searchDebounceTimer = null;
let skillsController = null;


// ==========================================
// 2. UTILITY FUNCTIONS
// ==========================================

// Mencegah HTML berbahaya masuk ke halaman
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}


// Mengambil CSRF token dari cookie atau input hidden
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (const item of cookies) {
            const cookie = item.trim();

            if (cookie.startsWith(`${name}=`)) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    if (!cookieValue) {
        cookieValue = document.querySelector(
            '[name=csrfmiddlewaretoken]'
        )?.value || null;
    }

    return cookieValue;
}


// Menampilkan notifikasi
function notify(title, message, type = 'info') {
    if (typeof showToast === 'function') {
        showToast(title, message, type);
    } else {
        alert(`${title}: ${message}`);
    }
}


// Mengubah error DRF menjadi pesan yang mudah dibaca
function getErrorMessage(data) {
    if (!data) {
        return 'Terjadi kesalahan pada server.';
    }

    if (typeof data.detail === 'string') {
        return data.detail;
    }

    if (typeof data === 'string') {
        return data;
    }

    return Object.entries(data)
        .map(([field, errors]) => {
            const messages = Array.isArray(errors)
                ? errors.join(', ')
                : String(errors);

            return `${field}: ${messages}`;
        })
        .join(' | ') || 'Terjadi kesalahan.';
}


// Mengambil JSON response dengan aman
async function readResponse(response) {
    const text = await response.text();

    if (!text) return {};

    try {
        return JSON.parse(text);
    } catch {
        return { detail: text };
    }
}


// ==========================================
// 3. FETCH SKILLS
// ==========================================

async function fetchSkills(name = '') {
    const skillsGrid = document.getElementById('skills-grid');
    const loadingState = document.getElementById('skills-loading');
    const emptyState = document.getElementById('skills-empty');
    const errorState = document.getElementById('skills-error');

    if (!skillsGrid) return;

    // Batalkan request pencarian sebelumnya
    if (skillsController) {
        skillsController.abort();
    }

    skillsController = new AbortController();

    const controller = skillsController;

    // Reset tampilan
    skillsGrid.innerHTML = '';

    if (loadingState) loadingState.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
    if (errorState) errorState.style.display = 'none';

    try {
        const url = name
            ? `${API_URL}?name=${encodeURIComponent(name)}`
            : API_URL;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            signal: controller.signal
        });

        const data = await readResponse(response);

        if (!response.ok) {
            throw new Error(getErrorMessage(data));
        }

        if (!Array.isArray(data)) {
            throw new Error('Format data Skill tidak sesuai.');
        }

        if (loadingState) loadingState.style.display = 'none';

        if (data.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        data.forEach(skill => {
            skillsGrid.appendChild(createSkillCard(skill));
        });

    } catch (error) {
        if (error.name === 'AbortError') return;

        console.error('Fetch skills error:', error);

        if (loadingState) loadingState.style.display = 'none';

        if (errorState) {
            errorState.style.display = 'block';
            errorState.textContent = error.message ||
                'Gagal memuat data Skill.';
        }
    }
}


// ==========================================
// 4. CREATE SKILL CARD
// ==========================================

function createSkillCard(skill) {
    const article = document.createElement('article');

    article.className = 'skill-card';

    // Tombol Star
    let starButton = '';

    if (skill.is_authenticated) {
        starButton = `
            <button
                type="button"
                class="button star-button"
                data-skill-id="${escapeHtml(skill.id)}"
            >
                ${skill.is_starred ? '★ Unstar' : '☆ Star'}
            </button>
        `;
    }

    // Tombol Edit
    let editButton = '';

    if (skill.can_update && skill.update_url) {
        editButton = `
            <a
                href="${escapeHtml(skill.update_url)}"
                class="button"
            >
                Edit
            </a>
        `;
    }

    // Tombol Delete
    let deleteButton = '';

    if (skill.can_delete) {
        deleteButton = `
            <button
                type="button"
                class="button button-danger delete-skill-button"
                data-skill-id="${escapeHtml(skill.id)}"
            >
                Hapus
            </button>
        `;
    }

    const proficiency = Math.min(
        100,
        Math.max(0, Number(skill.proficiency) || 0)
    );

    article.innerHTML = `
        <div class="skill-card-header">
            <div>
                <h2>${escapeHtml(skill.name)}</h2>

                <p class="skill-category">
                    ${escapeHtml(skill.category)}
                </p>
            </div>

            <span class="skill-proficiency">
                ${proficiency}%
            </span>
        </div>

        <div class="proficiency-info">
            <div class="proficiency-bar">
                <div
                    class="proficiency-fill"
                    style="--skill-width: ${proficiency}%;"
                ></div>
            </div>
        </div>

        <p class="skill-description">
            ${escapeHtml(skill.description)}
        </p>

        <p class="skill-stars">
            ⭐
            <span class="star-count">
                ${Number(skill.star_count) || 0}
            </span>
            Star
        </p>

        <div class="skill-actions">
            ${starButton}
            ${editButton}
            ${deleteButton}
        </div>
    `;

    // Event Star
    const starButtonElement =
        article.querySelector('.star-button');

    if (starButtonElement) {
        starButtonElement.addEventListener('click', () => {
            toggleStar(skill, article);
        });
    }

    // Event Delete
    const deleteButtonElement =
        article.querySelector('.delete-skill-button');

    if (deleteButtonElement) {
        deleteButtonElement.addEventListener('click', () => {
            deleteSkill(skill, article);
        });
    }

    return article;
}


// ==========================================
// 5. STAR / UNSTAR SKILL
// ==========================================

async function toggleStar(skill, article) {
    const button = article.querySelector('.star-button');
    const starCount = article.querySelector('.star-count');

    if (!button) return;

    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        notify('Error', 'CSRF token tidak ditemukan.', 'error');
        return;
    }

    try {
        button.disabled = true;

        const response = await fetch(
            `${API_URL}${skill.id}/star/`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                }
            }
        );

        const data = await readResponse(response);

        if (!response.ok) {
            throw new Error(getErrorMessage(data));
        }

        // API mengembalikan data Skill terbaru
        const updatedSkill = data.skill;

        if (!updatedSkill) {
            throw new Error('Respons Skill tidak ditemukan.');
        }

        // Perbarui jumlah Star
        if (starCount) {
            starCount.textContent = updatedSkill.star_count;
        }

        // Perbarui tombol
        button.textContent = updatedSkill.is_starred
            ? '★ Unstar'
            : '☆ Star';

        // Perbarui data lokal
        skill.is_starred = updatedSkill.is_starred;
        skill.star_count = updatedSkill.star_count;

        notify(
            'Berhasil',
            data.message || 'Status Star berhasil diperbarui.',
            'success'
        );

    } catch (error) {
        console.error('Star error:', error);

        notify('Gagal mengubah Star', error.message, 'error');

    } finally {
        button.disabled = false;
    }
}


// ==========================================
// 6. DELETE SKILL
// ==========================================

async function deleteSkill(skill, article) {
    const confirmed = confirm(
        `Yakin ingin menghapus skill "${skill.name}"?`
    );

    if (!confirmed) return;

    const button = article.querySelector('.delete-skill-button');
    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        notify('Error', 'CSRF token tidak ditemukan.', 'error');
        return;
    }

    try {
        if (button) button.disabled = true;

        const response = await fetch(
            `${API_URL}${skill.id}/`,
            {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            }
        );

        if (!response.ok) {
            const data = await readResponse(response);
            throw new Error(getErrorMessage(data));
        }

        // Hapus kartu dari halaman
        article.remove();

        notify(
            'Berhasil',
            'Skill berhasil dihapus!',
            'success'
        );

        // Periksa apakah masih ada Skill
        const skillsGrid = document.getElementById('skills-grid');
        const emptyState = document.getElementById('skills-empty');

        if (skillsGrid && skillsGrid.children.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
        }

    } catch (error) {
        console.error('Delete skill error:', error);

        notify('Gagal menghapus Skill', error.message, 'error');

    } finally {
        if (button && button.isConnected) {
            button.disabled = false;
        }
    }
}


// ==========================================
// 7. CLOSE ADD SKILL MODAL
// ==========================================

function closeSkillModal() {
    const modal = document.getElementById('add-skill-modal');

    if (modal && modal.matches(':popover-open')) {
        modal.hidePopover();
    }
}


// ==========================================
// 8. ADD SKILL
// ==========================================

async function addSkill(event) {
    event.preventDefault();

    const form = event.currentTarget;

    const submitButton = form.querySelector(
        'button[type="submit"]'
    );

    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        notify('Error', 'CSRF token tidak ditemukan.', 'error');
        return;
    }

    try {
        if (submitButton) submitButton.disabled = true;

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'
            },
            body: new FormData(form)
        });

        const data = await readResponse(response);

        if (!response.ok) {
            throw new Error(getErrorMessage(data));
        }

        form.reset();

        closeSkillModal();

        notify(
            'Berhasil',
            'Skill baru berhasil ditambahkan!',
            'success'
        );

        // Muat ulang data tanpa reload halaman
        const searchInput = document.querySelector(
            '.skill-search__input'
        );

        fetchSkills(searchInput?.value.trim() || '');

    } catch (error) {
        console.error('Add skill error:', error);

        notify(
            'Gagal menambahkan Skill',
            error.message,
            'error'
        );

    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}


// ==========================================
// 9. EDIT SKILL
// ==========================================

async function editSkill(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const skillId = form.dataset.skillId;

    // Tidak ada ID berarti form bukan untuk Edit
    if (!skillId) return;

    const submitButton = form.querySelector(
        'button[type="submit"]'
    );

    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        notify('Error', 'CSRF token tidak ditemukan.', 'error');
        return;
    }

    try {
        if (submitButton) submitButton.disabled = true;

        // Ubah FormData menjadi JSON
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Hapus field CSRF dari data JSON
        delete data.csrfmiddlewaretoken;

        const response = await fetch(
            `${API_URL}${skillId}/`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            }
        );

        const result = await readResponse(response);

        if (!response.ok) {
            throw new Error(getErrorMessage(result));
        }

        notify(
            'Berhasil',
            'Skill berhasil diperbarui!',
            'success'
        );

        // Kembali ke halaman Skills
        window.location.href = '/skills/';

    } catch (error) {
        console.error('Edit skill error:', error);

        notify(
            'Gagal memperbarui Skill',
            error.message,
            'error'
        );

    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}


// ==========================================
// 10. INITIALIZE EVENT LISTENERS
// ==========================================

document.addEventListener('DOMContentLoaded', () => {

    // Ambil daftar Skill
    fetchSkills();

    // Form Add melalui modal
    const addForm = document.getElementById('skill-form');

    if (addForm) {
        addForm.addEventListener('submit', addSkill);
    }

    // Form Edit melalui halaman skill_form.html
    const editForm = document.getElementById('skill-edit-form');

    if (editForm && editForm.dataset.skillId) {
        editForm.addEventListener('submit', editSkill);
    }

    // Search Skill
    const searchForm = document.querySelector('.skill-search');
    const searchInput = document.querySelector(
        '.skill-search__input'
    );

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchDebounceTimer);

            searchDebounceTimer = setTimeout(() => {
                fetchSkills(searchInput.value.trim());
            }, SEARCH_DEBOUNCE_DELAY);
        });
    }

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', event => {
            event.preventDefault();

            clearTimeout(searchDebounceTimer);

            fetchSkills(searchInput.value.trim());
        });
    }
});

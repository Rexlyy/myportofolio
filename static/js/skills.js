function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}


async function fetchSkills(name = '') {
    const skillsGrid = document.getElementById('skills-grid');
    const loadingState = document.getElementById('skills-loading');
    const emptyState = document.getElementById('skills-empty');
    const errorState = document.getElementById('skills-error');

    if (!skillsGrid) return;

    // Reset tampilan
    skillsGrid.innerHTML = '';
    loadingState.style.display = 'block';
    emptyState.style.display = 'none';
    errorState.style.display = 'none';

    try {
        const url = name
            ? `/api/skills/?name=${encodeURIComponent(name)}`
            : '/api/skills/';

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Gagal mengambil data Skill.');
        }

        const data = await response.json();

        loadingState.style.display = 'none';

        if (!data.skills || data.skills.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        data.skills.forEach(skill => {
            skillsGrid.appendChild(createSkillCard(skill));
        });

    } catch (error) {
        console.error(error);

        loadingState.style.display = 'none';
        errorState.style.display = 'block';
        errorState.textContent = 'Gagal memuat data Skill.';
    }
}


function createSkillCard(skill) {
    const article = document.createElement('article');

    article.className = 'skill-card';

    let starButton = '';

    if (skill.is_authenticated) {
        starButton = `
            <button
                type="button"
                class="button star-button"
                data-skill-id="${skill.id}"
            >
                ${skill.is_starred ? '★ Unstar' : '☆ Star'}
            </button>
        `;
    }

    article.innerHTML = `
        <div class="skill-card-header">

            <div>
                <h2>${escapeHtml(skill.name)}</h2>

                <p class="skill-category">
                    ${escapeHtml(skill.category)}
                </p>
            </div>

            <span class="skill-proficiency">
                ${Number(skill.proficiency)}%
            </span>

        </div>

        <div class="proficiency-info">
            <div class="proficiency-bar">
                <div
                    class="proficiency-fill"
                    style="--skill-width: ${Number(skill.proficiency)}%;"
                ></div>
            </div>
        </div>

        <p class="skill-description">
            ${escapeHtml(skill.description)}
        </p>

        <p class="skill-stars">
            ⭐ <span class="star-count">${Number(skill.star_count)}</span> Star
        </p>

        <div class="skill-actions">
        
            ${starButton}

            ${
                skill.is_superuser
                    ? `
                        <a
                            href="/skills/${skill.id}/update/"
                            class="button"
                        >
                            Edit
                        </a>

                        <a
                            href="/skills/${skill.id}/delete/"
                            class="button button-danger"
                        >
                            Hapus
                        </a>
                    `
                    : ''
            }
        </div>
    `;

    const starButtonElement =
        article.querySelector('.star-button');

    if (starButtonElement) {
        starButtonElement.addEventListener('click', () => {
            toggleStar(skill, article);
        });
    }

    return article;
}

async function toggleStar(skill, article) {
    const button = article.querySelector('.star-button');
    const starCount = article.querySelector('.star-count');

    if (!button) {
        return;
    }

    const csrfToken = document.querySelector(
        '[name=csrfmiddlewaretoken]'
    )?.value;

    if (!csrfToken) {
        showToast(
            'Error',
            'CSRF token tidak ditemukan.',
            'error'
        );
        return;
    }

    try {
        button.disabled = true;

        const response = await fetch(
            `/skills/${skill.id}/star/`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP error: ${response.status}`
            );
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(
                data.error || 'Gagal mengubah Star.'
            );
        }

        // Update jumlah Star
        starCount.textContent = data.star_count;

        // Update tombol
        button.textContent = data.is_starred
            ? '★ Unstar'
            : '☆ Star';

        // Update data lokal
        skill.is_starred = data.is_starred;
        skill.star_count = data.star_count;

        showToast(
            'Berhasil',
            data.message,
            'success'
        );

    } catch (error) {
        console.error(error);

        showToast(
            'Error',
            'Gagal mengubah status Star.',
            'error'
        );

    } finally {
        button.disabled = false;
    }
}

const SEARCH_DEBOUNCE_DELAY = 300;

let searchDebounceTimer;

const skillForm = document.getElementById('skill-form');


function closeSkillModal() {
    const modal = document.getElementById('add-skill-modal');

    if (modal && modal.matches(':popover-open')) {
        modal.hidePopover();
    }
}


function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {

        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (
                cookie.substring(0, name.length + 1)
                === (name + '=')
            ) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


async function addSkill(event) {

    event.preventDefault();

    if (!skillForm) {
        return;
    }

    const submitButton =
        skillForm.querySelector(
            'button[type="submit"]'
        );

    submitButton.disabled = true;

    try {

        const response = await fetch(
            skillForm.action,
            {
                method: 'POST',

                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },

                body: new FormData(skillForm)
            }
        );

        const result =
            await response.json().catch(() => ({}));


        if (response.ok) {

            skillForm.reset();

            closeSkillModal();

            showToast(
                'Berhasil',
                'Skill baru berhasil ditambahkan!',
                'success'
            );

            fetchSkills(
                document
                    .querySelector('.skill-search__input')
                    ?.value.trim() || ''
            );

        } else {

            const errorMessages = result.errors
                ? Object.values(result.errors)
                    .flat()
                    .map(error => error.message)
                : [
                    result.message ||
                    `Terjadi kesalahan (status ${response.status}).`
                ];

            showToast(
                'Gagal menambahkan Skill',
                errorMessages.join(' '),
                'error'
            );
        }

    } catch (error) {

        console.error(
            'Error adding skill:',
            error
        );

        showToast(
            'Gagal menambahkan Skill',
            'Tidak dapat terhubung ke server. Silakan coba lagi.',
            'error'
        );

    } finally {

        submitButton.disabled = false;

    }
}


document.addEventListener('DOMContentLoaded', () => {
    fetchSkills();

    if (skillForm) {
    skillForm.addEventListener(
        'submit',
        addSkill
    );
    }

    const searchForm = document.querySelector('.skill-search');
    const searchInput = document.querySelector('.skill-search__input');

    if (!searchForm || !searchInput) {
        return;
    }


    searchInput.addEventListener('input', () => {

        clearTimeout(searchDebounceTimer);

        searchDebounceTimer = setTimeout(() => {
            fetchSkills(searchInput.value.trim());
        }, SEARCH_DEBOUNCE_DELAY);

    });


    searchForm.addEventListener('submit', (event) => {

        event.preventDefault();

        clearTimeout(searchDebounceTimer);

        fetchSkills(searchInput.value.trim());

    });

});
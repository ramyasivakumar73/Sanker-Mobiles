document.addEventListener('DOMContentLoaded', function() {
    // Live Search Functionality
    const searchInput = document.getElementById('productSearch');
    const productCards = document.querySelectorAll('.product-card');
    const categoryButtons = document.querySelectorAll('.btn-category');

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            filterProducts(searchTerm, getActiveCategory());
        });
    }

    if (categoryButtons) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                const category = this.getAttribute('data-category');
                const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
                filterProducts(searchTerm, category);
            });
        });
    }

    function getActiveCategory() {
        const activeBtn = document.querySelector('.btn-category.active');
        return activeBtn ? activeBtn.getAttribute('data-category') : 'all';
    }

    function filterProducts(searchTerm, category) {
        productCards.forEach(card => {
            const name = card.getAttribute('data-name').toLowerCase();
            const brand = card.getAttribute('data-brand').toLowerCase();
            const productCategory = card.getAttribute('data-category');

            const matchesSearch = name.includes(searchTerm) || brand.includes(searchTerm);
            const matchesCategory = category === 'all' || productCategory === category;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'block';
                card.classList.add('fade-in');
            } else {
                card.style.display = 'none';
                card.classList.remove('fade-in');
            }
        });
    }

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
            navbar.style.padding = '0.5rem 0';
        } else {
            navbar.style.boxShadow = 'none';
            navbar.style.padding = '1rem 0';
        }
    });
});

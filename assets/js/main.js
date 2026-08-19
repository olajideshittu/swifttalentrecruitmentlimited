
        function showArticle(id) {
            document.querySelectorAll('.full-article').forEach(article => article.classList.remove('active'));
            document.getElementById(`article-${id}`).classList.add('active');
            document.getElementById(`article-${id}`).scrollIntoView({ behavior: 'smooth' });
        }

        function backToBlog() {
            document.querySelectorAll('.full-article').forEach(article => article.classList.remove('active'));
            document.getElementById('blog').scrollIntoView({ behavior: 'smooth' });
        }

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                if (this.getAttribute('href') === '#') return;
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({ behavior: 'smooth' });
            });
        });
    

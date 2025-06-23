document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-toggle-role').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Mencegah form disubmit secara default

            const userId = this.dataset.userId;
            const username = this.dataset.username;
            const currentRole = this.dataset.currentRole;
            const toggleRoleUrl = this.dataset.toggleRoleUrl;

            let newRoleText = '';
            if (currentRole === 'admin') {
                newRoleText = 'pelanggan';
            } else {
                newRoleText = 'admin';
            }

            if (confirm(`Apakah Anda yakin ingin mengubah peran ${username} menjadi ${newRoleText}?`)) {
                // Membuat form dinamis untuk submit POST
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = toggleRoleUrl;
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
});
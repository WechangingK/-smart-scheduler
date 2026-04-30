// Toast 通知
function showToast(message, type = 'info') {
	const container = document.querySelector('.toast-container') || createToastContainer();
	const toast = document.createElement('div');
	toast.className = `toast toast-${type}`;
	toast.textContent = message;
	container.appendChild(toast);
	setTimeout(() => {
		toast.style.opacity = '0';
		toast.style.transform = 'translateX(100%)';
		toast.style.transition = 'all 0.3s ease';
		setTimeout(() => toast.remove(), 300);
	}, 3000);
}

function createToastContainer() {
	const container = document.createElement('div');
	container.className = 'toast-container';
	document.body.appendChild(container);
	return container;
}

// Modal 工具
function openModal(title, contentHtml, onSave) {
	const overlay = document.createElement('div');
	overlay.className = 'modal-overlay';
	overlay.innerHTML = `
		<div class="modal">
			<div class="modal-header">
				<h3>${title}</h3>
				<button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
			</div>
			<div class="modal-body">${contentHtml}</div>
			<div class="modal-footer">
				<button class="btn" onclick="this.closest('.modal-overlay').remove()">取消</button>
				<button class="btn btn-primary save-btn">保存</button>
			</div>
		</div>
	`;
	document.body.appendChild(overlay);

	if (onSave) {
		overlay.querySelector('.save-btn').addEventListener('click', () => {
			onSave(overlay);
		});
	}

	overlay.addEventListener('click', (e) => {
		if (e.target === overlay) overlay.remove();
	});
}

// API 请求封装
async function api(url, options = {}) {
	const defaultHeaders = {
		'Content-Type': 'application/json',
		...(options.headers || {}),
	};
	const res = await fetch(url, {
		...options,
		headers: defaultHeaders,
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({ error: '请求失败' }));
		throw new Error(err.error || '请求失败');
	}
	return res.json();
}

// 格式化日期
function formatDate(isoStr) {
	if (!isoStr) return '';
	const d = new Date(isoStr);
	return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

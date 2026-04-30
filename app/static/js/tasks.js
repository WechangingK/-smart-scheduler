// 加载任务列表
async function loadTasks() {
	const status = document.getElementById('filterStatus').value;
	const category = document.getElementById('filterCategory').value;
	const params = new URLSearchParams();
	if (status) params.append('status', status);
	if (category) params.append('category', category);

	try {
		const tasks = await api(`/api/tasks?${params.toString()}`);
		renderTaskTable(tasks);
	} catch (e) {
		showToast('加载任务失败: ' + e.message, 'error');
	}
}

function renderTaskTable(tasks) {
	const tbody = document.querySelector('#taskTable tbody');
	if (tasks.length === 0) {
		tbody.innerHTML = '<tr><td colspan="7" class="empty-hint">暂无任务</td></tr>';
		return;
	}

	const priorityLabels = { high: '高', medium: '中', low: '低' };
	tbody.innerHTML = tasks.map(t => `
		<tr>
			<td><strong>${escapeHtml(t.title)}</strong></td>
			<td><span class="badge badge-${t.priority}">${priorityLabels[t.priority] || t.priority}</span></td>
			<td>${t.category || '-'}</td>
			<td>${formatDate(t.due_date) || '-'}</td>
			<td>${t.estimated_minutes ? t.estimated_minutes + '分钟' : '-'}</td>
			<td>${t.status}</td>
			<td class="actions">
				${t.status === 'pending' ? `<button class="btn btn-sm" onclick="completeTask(${t.id})">✓完成</button>` : ''}
				<button class="btn btn-sm" onclick="openTaskModal(${t.id})">编辑</button>
				<button class="btn btn-sm btn-danger" onclick="deleteTask(${t.id})">删除</button>
			</td>
		</tr>
	`).join('');
}

function openTaskModal(taskId = null) {
	const isEdit = taskId !== null;
	const title = isEdit ? '编辑任务' : '新建任务';

	const contentHtml = `
		<div class="form-group">
			<label class="form-label">标题 *</label>
			<input type="text" id="taskTitle" class="form-input" placeholder="任务标题">
		</div>
		<div class="form-group">
			<label class="form-label">描述</label>
			<textarea id="taskDesc" class="form-textarea" rows="3" placeholder="任务描述"></textarea>
		</div>
		<div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
			<div class="form-group">
				<label class="form-label">优先级</label>
				<select id="taskPriority" class="form-select">
					<option value="high">高</option>
					<option value="medium" selected>中</option>
					<option value="low">低</option>
				</select>
			</div>
			<div class="form-group">
				<label class="form-label">分类</label>
				<select id="taskCategory" class="form-select">
					<option value="">无</option>
					<option value="工作">工作</option>
					<option value="学习">学习</option>
					<option value="健康">健康</option>
					<option value="生活">生活</option>
				</select>
			</div>
			<div class="form-group">
				<label class="form-label">截止时间</label>
				<input type="datetime-local" id="taskDueDate" class="form-input">
			</div>
			<div class="form-group">
				<label class="form-label">预估时间（分钟）</label>
				<input type="number" id="taskEstMinutes" class="form-input" placeholder="60">
			</div>
			<div class="form-group">
				<label class="form-label">所需精力</label>
				<select id="taskEnergy" class="form-select">
					<option value="">不限</option>
					<option value="high">高</option>
					<option value="medium">中</option>
					<option value="low">低</option>
				</select>
			</div>
		</div>
	`;

	const onSave = async (overlay) => {
		const data = {
			title: overlay.querySelector('#taskTitle').value,
			description: overlay.querySelector('#taskDesc').value,
			priority: overlay.querySelector('#taskPriority').value,
			category: overlay.querySelector('#taskCategory').value || null,
			due_date: overlay.querySelector('#taskDueDate').value || null,
			estimated_minutes: parseInt(overlay.querySelector('#taskEstMinutes').value) || null,
			energy_level: overlay.querySelector('#taskEnergy').value || null,
		};

		if (!data.title) {
			showToast('请输入任务标题', 'error');
			return;
		}

		try {
			if (isEdit) {
				await api(`/api/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify(data) });
				showToast('任务已更新', 'success');
			} else {
				await api('/api/tasks', { method: 'POST', body: JSON.stringify(data) });
				showToast('任务已创建', 'success');
			}
			overlay.remove();
			loadTasks();
		} catch (e) {
			showToast('保存失败: ' + e.message, 'error');
		}
	};

	openModal(title, contentHtml, onSave);

	if (isEdit) {
		api(`/api/tasks/${taskId}`).then(task => {
			const overlay = document.querySelector('.modal-overlay');
			if (!overlay) return;
			overlay.querySelector('#taskTitle').value = task.title || '';
			overlay.querySelector('#taskDesc').value = task.description || '';
			overlay.querySelector('#taskPriority').value = task.priority || 'medium';
			overlay.querySelector('#taskCategory').value = task.category || '';
			if (task.due_date) {
				const d = new Date(task.due_date);
				overlay.querySelector('#taskDueDate').value = d.toISOString().slice(0, 16);
			}
			overlay.querySelector('#taskEstMinutes').value = task.estimated_minutes || '';
			overlay.querySelector('#taskEnergy').value = task.energy_level || '';
		});
	}
}

async function completeTask(taskId) {
	try {
		await api(`/api/tasks/${taskId}/complete`, { method: 'POST' });
		showToast('任务已完成 ✅', 'success');
		loadTasks();
	} catch (e) {
		showToast('操作失败: ' + e.message, 'error');
	}
}

async function deleteTask(taskId) {
	if (!confirm('确定删除这个任务吗？')) return;
	try {
		await api(`/api/tasks/${taskId}`, { method: 'DELETE' });
		showToast('任务已删除', 'info');
		loadTasks();
	} catch (e) {
		showToast('删除失败: ' + e.message, 'error');
	}
}

function escapeHtml(str) {
	const div = document.createElement('div');
	div.textContent = str;
	return div.innerHTML;
}

// 页面加载时加载任务
loadTasks();

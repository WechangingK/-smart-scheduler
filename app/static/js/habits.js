// 加载习惯列表
async function loadHabits() {
	const date = document.getElementById('habitDate').value;
	try {
		const habits = await api(`/api/habits?date=${date}`);
		renderHabitList(habits);
	} catch (e) {
		showToast('加载习惯数据失败: ' + e.message, 'error');
	}
}

function renderHabitList(habits) {
	const container = document.getElementById('habitList');
	if (habits.length === 0) {
		container.innerHTML = '<p class="empty-hint">今日暂无打卡记录，点击"打卡"开始</p>';
		return;
	}

	container.innerHTML = `
		<ul class="habit-checklist">
			${habits.map(h => `
				<li class="habit-item ${h.completed ? 'completed' : ''}">
					<div>
						<span class="habit-name">${escapeHtml(h.name)}</span>
						${h.notes ? `<span style="font-size:12px;color:#8892a4;margin-left:8px;">${escapeHtml(h.notes)}</span>` : ''}
						${h.value ? `<span style="font-size:12px;color:#4a6cf7;margin-left:8px;">${h.value}</span>` : ''}
					</div>
					<div style="display:flex;gap:8px;align-items:center;">
						<span class="habit-status" style="cursor:pointer;font-size:18px;"
							onclick="toggleHabit('${escapeHtml(h.name)}', ${!h.completed})">
							${h.completed ? '✅' : '⬜'}
						</span>
					</div>
				</li>
			`).join('')}
		</ul>
	`;
}

function openHabitModal() {
	const contentHtml = `
		<div class="form-group">
			<label class="form-label">习惯名称 *</label>
			<input type="text" id="habitName" class="form-input" placeholder="例如：晨跑、阅读、冥想">
		</div>
		<div class="form-group">
			<label class="form-label">日期</label>
			<input type="date" id="habitModalDate" class="form-input" value="${document.getElementById('habitDate').value}">
		</div>
		<div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
			<div class="form-group">
				<label class="form-label">是否完成</label>
				<select id="habitCompleted" class="form-select">
					<option value="true">✅ 已完成</option>
					<option value="false">⬜ 未完成</option>
				</select>
			</div>
			<div class="form-group">
				<label class="form-label">量化值（可选）</label>
				<input type="number" id="habitValue" class="form-input" placeholder="如 5.0 (公里)">
			</div>
		</div>
		<div class="form-group">
			<label class="form-label">备注</label>
			<input type="text" id="habitNotes" class="form-input" placeholder="备注信息">
		</div>
	`;

	const onSave = async (overlay) => {
		const data = {
			name: overlay.querySelector('#habitName').value,
			date: overlay.querySelector('#habitModalDate').value,
			completed: overlay.querySelector('#habitCompleted').value === 'true',
			value: parseFloat(overlay.querySelector('#habitValue').value) || null,
			notes: overlay.querySelector('#habitNotes').value || null,
		};

		if (!data.name) {
			showToast('请输入习惯名称', 'error');
			return;
		}

		try {
			await api('/api/habits', { method: 'POST', body: JSON.stringify(data) });
			showToast('打卡成功！', 'success');
			overlay.remove();
			loadHabits();
		} catch (e) {
			showToast('打卡失败: ' + e.message, 'error');
		}
	};

	openModal('新增习惯打卡', contentHtml, onSave);
}

async function toggleHabit(name, completed) {
	const date = document.getElementById('habitDate').value;
	try {
		await api('/api/habits', {
			method: 'POST',
			body: JSON.stringify({ name, date, completed }),
		});
		loadHabits();
	} catch (e) {
		showToast('操作失败: ' + e.message, 'error');
	}
}

async function loadHabitStats() {
	try {
		const stats = await api('/api/habits/stats');
		const container = document.getElementById('habitStats');
		if (!stats || stats.length === 0) {
			container.innerHTML = '<p class="empty-hint">暂无习惯数据</p>';
			return;
		}

		const trendLabels = { up: '📈 上升', down: '📉 下降', stable: '➡️ 稳定' };
		container.innerHTML = `
			<table class="data-table">
				<thead><tr><th>习惯</th><th>完成率</th><th>连续天数</th><th>趋势</th><th>平均值</th></tr></thead>
				<tbody>
					${stats.map(s => `
						<tr>
							<td><strong>${escapeHtml(s.name)}</strong></td>
							<td>${Math.round(s.completion_rate * 100)}%</td>
							<td>${s.streak} 天</td>
							<td>${trendLabels[s.trend] || s.trend}</td>
							<td>${s.average_value || '-'}</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		`;
	} catch (e) {
		showToast('加载统计失败: ' + e.message, 'error');
	}
}

async function loadAIAnalysis() {
	const btn = event.target;
	btn.disabled = true;
	btn.textContent = '分析中...';
	try {
		const result = await api('/api/habits/analyze');
		const container = document.getElementById('aiAnalysis');

		if (result.ai_analysis) {
			const analysis = result.ai_analysis;
			let html = '';
			if (analysis.overall_assessment) {
				html += `<p style="margin-bottom:12px;"><strong>📝 整体评价：</strong>${analysis.overall_assessment}</p>`;
			}
			if (analysis.habits) {
				html += '<ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">';
				analysis.habits.forEach(h => {
					html += `<li style="padding:8px 12px;background:#f8f9fc;border-radius:8px;">
						<strong>${escapeHtml(h.name)}</strong>: ${escapeHtml(h.suggestion)}</li>`;
				});
				html += '</ul>';
			}
			if (analysis.next_week_focus) {
				html += `<p style="margin-top:12px;"><strong>🎯 下周重点：</strong>${analysis.next_week_focus}</p>`;
			}
			container.innerHTML = html;
		} else {
			container.innerHTML = '<p class="empty-hint">AI 分析暂不可用，请先配置 DeepSeek API Key</p>';
		}
	} catch (e) {
		showToast('AI 分析失败: ' + e.message, 'error');
	}
	btn.disabled = false;
	btn.textContent = 'AI 分析';
}

function escapeHtml(str) {
	const div = document.createElement('div');
	div.textContent = str;
	return div.innerHTML;
}

// 初始化日期和加载
document.getElementById('habitDate').value = new Date().toISOString().split('T')[0];
loadHabits();

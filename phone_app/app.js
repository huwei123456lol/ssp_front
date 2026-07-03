const API_TASKS_URL = '/api/tasks';
const API_ACCOUNT_URL = '/api/account';
const taskList = document.getElementById('taskList');
const taskCount = document.getElementById('taskCount');
const waitingCount = document.getElementById('waitingCount');
const pendingCount = document.getElementById('pendingCount');
const doneCount = document.getElementById('doneCount');
const planName = document.getElementById('planName');
const planDetail = document.getElementById('planDetail');
const renewDate = document.getElementById('renewDate');
const renewStatus = document.getElementById('renewStatus');
const featureTags = document.getElementById('featureTags');
const planStatus = document.getElementById('planStatus');
const buttons = document.querySelectorAll('.nav-btn');
const headerBtn = document.querySelector('.header-btn');

buttons.forEach((btn) => {
  btn.addEventListener('click', () => {
    buttons.forEach((item) => item.classList.remove('active'));
    btn.classList.add('active');
  });
});

headerBtn.addEventListener('click', () => {
  alert('调用后端新建任务接口，可在此处扩展新增功能。');
});

function formatStatusLabel(status) {
  if (status === 'done') return '已完成';
  if (status === 'pending') return '进行中';
  return '待办';
}

function addTask(title, note, status) {
  const li = document.createElement('li');
  li.className = 'task-item';
  li.innerHTML = `
    <div>
      <strong>${title}</strong>
      <p>${note}</p>
    </div>
    <span class="status ${status}">${formatStatusLabel(status)}</span>
  `;
  taskList.appendChild(li);
}

function updateSummary(tasks) {
  const counts = { waiting: 0, pending: 0, done: 0 };
  tasks.forEach((task) => {
    const key = task.status === 'done' ? 'done' : task.status === 'pending' ? 'pending' : 'waiting';
    counts[key] += 1;
  });

  waitingCount.textContent = counts.waiting;
  pendingCount.textContent = counts.pending;
  doneCount.textContent = counts.done;
  taskCount.textContent = `${tasks.length} 条`;
}

function renderTasks(tasks) {
  taskList.innerHTML = '';
  tasks.forEach(({ title, note, status }) => addTask(title, note, status));
  updateSummary(tasks);
}

function renderAccount(account) {
  planName.textContent = account.plan || '免费版';
  planDetail.textContent = account.note || '基础 SaaS 功能';
  renewDate.textContent = account.nextRenew || '--';
  renewStatus.textContent = account.status === 'active' ? '已激活' : '已暂停';
  planStatus.textContent = account.status === 'active' ? '运行中' : '暂停';
  featureTags.textContent = account.features?.join(' · ') || '基础版功能 · 数据报表 · 团队协作';
}

async function fetchTasks() {
  try {
    const response = await fetch(API_TASKS_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`接口返回错误：${response.status}`);
    }

    const result = await response.json();
    const tasks = Array.isArray(result) ? result : result.tasks || [];

    if (tasks.length === 0) {
      renderTasks([
        { title: '暂无任务', note: '当前没有可加载的任务。', status: 'waiting' },
      ]);
      return;
    }

    renderTasks(tasks);
  } catch (error) {
    console.error('获取任务失败：', error);
    renderTasks([
      { title: '无法获取任务', note: '请检查后端服务是否已启动', status: 'waiting' },
    ]);
  }
}

async function fetchAccount() {
  try {
    const response = await fetch(API_ACCOUNT_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`账户接口错误：${response.status}`);
    }

    const result = await response.json();
    renderAccount(result);
  } catch (error) {
    console.error('获取账户信息失败：', error);
    renderAccount({
      plan: '免费版',
      note: '基础 SaaS 功能访问',
      nextRenew: '无',
      status: 'inactive',
      features: ['基础功能', '限时试用'],
    });
  }
}

fetchAccount();
fetchTasks();

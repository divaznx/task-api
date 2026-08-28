const listEl = document.getElementById("task-list");
const emptyEl = document.getElementById("empty");
const statusEl = document.getElementById("status");
const formEl = document.getElementById("create-form");
const titleEl = document.getElementById("title");
const descriptionEl = document.getElementById("description");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

async function request(path, options = {}) {
  const { headers, ...rest } = options;
  const response = await fetch(path, {
    ...rest,
    headers: { "Content-Type": "application/json", ...headers },
  });

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error("The API returned an unexpected response.");
    }
  }

  if (data && data.error) {
    throw new Error(data.error);
  }

  if (!response.ok) {
    const detail =
      (data && (data.detail || data.message)) || `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

function renderTasks(tasks) {
  listEl.replaceChildren();
  emptyEl.hidden = tasks.length > 0;

  for (const task of tasks) {
    const item = document.createElement("li");
    item.className = "task" + (task.completed ? " done" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = Boolean(task.completed);
    checkbox.setAttribute("aria-label", `Mark "${task.title}" complete`);
    checkbox.addEventListener("change", () => toggleComplete(task.id, checkbox.checked));

    const body = document.createElement("div");
    const title = document.createElement("p");
    title.className = "task-title";
    title.textContent = task.title || "(untitled)";
    body.append(title);

    if (task.description) {
      const desc = document.createElement("p");
      desc.className = "task-desc";
      desc.textContent = task.description;
      body.append(desc);
    }

    const del = document.createElement("button");
    del.type = "button";
    del.textContent = "Delete";
    del.addEventListener("click", () => deleteTask(task.id));

    item.append(checkbox, body, del);
    listEl.append(item);
  }
}

async function loadTasks() {
  setStatus("Loading…");
  try {
    const data = await request("/tasks");
    const tasks = Array.isArray(data.tasks) ? data.tasks : [];
    renderTasks(tasks);
    setStatus(tasks.length ? `${tasks.length} task${tasks.length === 1 ? "" : "s"}` : "");
  } catch (err) {
    renderTasks([]);
    emptyEl.hidden = true;
    setStatus(err.message, true);
  }
}

async function toggleComplete(id, completed) {
  try {
    await request(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    });
    await loadTasks();
  } catch (err) {
    setStatus(err.message, true);
    await loadTasks();
  }
}

async function deleteTask(id) {
  try {
    await request(`/tasks/${id}`, { method: "DELETE" });
    await loadTasks();
  } catch (err) {
    setStatus(err.message, true);
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleEl.value.trim();
  if (!title) {
    setStatus("Title is required.", true);
    return;
  }

  const description = descriptionEl.value.trim();
  const payload = { title };
  if (description) {
    payload.description = description;
  }

  try {
    await request("/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    formEl.reset();
    titleEl.focus();
    await loadTasks();
  } catch (err) {
    setStatus(err.message, true);
  }
});

loadTasks();

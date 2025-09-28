const searchInput = document.getElementById("search-input");
const verifyToggle = document.getElementById("verify-toggle");
const topicFilter = document.getElementById("topic-filter");
const searchButton = document.getElementById("search-btn");
const statusNode = document.getElementById("status");
const resultsNode = document.getElementById("results");
const cardTemplate = document.getElementById("card-template");

const state = {
  isLoading: false,
  lastQuery: "",
  topicsLoaded: false
};

function setStatus(message, tone = "info") {
  statusNode.textContent = message;
  statusNode.dataset.tone = tone;
}

function setBusy(isBusy) {
  state.isLoading = isBusy;
  resultsNode.setAttribute("aria-busy", String(isBusy));
  searchButton.disabled = isBusy;
}

async function fetchJSON(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed (${response.status}): ${text.slice(0, 120)}`);
  }
  return response.json();
}

async function loadTopics() {
  if (state.topicsLoaded) {
    return;
  }
  try {
    const topics = await fetchJSON("/api/topics");
    populateTopics(topics);
    state.topicsLoaded = true;
  } catch (error) {
    console.warn("Unable to fetch topics", error);
  }
}

function populateTopics(topics) {
  const fragment = document.createDocumentFragment();
  for (const topic of topics) {
    const option = document.createElement("option");
    option.value = topic.name;
    option.textContent = `${topic.name} (${topic.count})`;
    fragment.appendChild(option);
  }
  topicFilter.appendChild(fragment);
}

function formatMeta(item) {
  const parts = [];
  if (item.journal) parts.push(item.journal);
  if (item.year) parts.push(String(item.year));
  if (item.topics?.length) parts.push(item.topics.join(", "));
  return parts.join(" • ");
}

function formatAuthors(authors) {
  if (!authors || authors.length === 0) {
    return "";
  }
  return `Authors: ${authors.join(", ")}`;
}

function buildActionButtons(item, descriptor) {
  const actions = document.createElement("div");
  actions.className = "actions";

  const openBtn = document.createElement("button");
  if (descriptor.usable && descriptor.url) {
    openBtn.textContent = `Open ${descriptor.label}`;
    openBtn.addEventListener("click", () => {
      window.open(descriptor.url, "_blank", "noopener");
    });
  } else {
    openBtn.textContent = "Identifier unavailable";
    openBtn.disabled = true;
  }
  actions.appendChild(openBtn);

  if (item.source_url) {
    const sourceLink = document.createElement("a");
    sourceLink.textContent = "View source";
    sourceLink.href = item.source_url;
    sourceLink.target = "_blank";
    sourceLink.rel = "noopener";
    actions.appendChild(sourceLink);
  }

  return actions;
}

function buildCard(item) {
  const node = cardTemplate.content.firstElementChild.cloneNode(true);
  const descriptor = item.identifier;

  node.querySelector(".card-title").textContent = item.title;
  node.querySelector(".card-summary").textContent = item.summary;

  const metaText = formatMeta(item);
  node.querySelector(".card-meta").textContent = metaText;

  const authorsText = formatAuthors(item.authors);
  const authorsNode = node.querySelector(".card-authors");
  if (authorsText) {
    authorsNode.textContent = authorsText;
  } else {
    authorsNode.remove();
  }

  const badge = node.querySelector(".badge");
  badge.dataset.type = descriptor.type;
  badge.textContent = descriptor.display_text;

  const actions = buildActionButtons(item, descriptor);
  const actionsContainer = node.querySelector(".actions");
  actionsContainer.replaceWith(actions);

  const warning = node.querySelector(".identifier-warning");
  if (item.doi_error && item.original_doi) {
    warning.hidden = false;
    warning.textContent = `DOI ${item.original_doi} could not be reached. Showing ${descriptor.label} instead.`;
  }

  node.querySelector(".viva").textContent = item.viva_prompt;

  return node;
}

function renderResults(results) {
  resultsNode.innerHTML = "";
  if (!results.length) {
    const empty = document.createElement("p");
    empty.textContent = "No evidence found. Try a different keyword or remove filters.";
    empty.className = "empty-state";
    resultsNode.appendChild(empty);
    return;
  }

  const fragment = document.createDocumentFragment();
  for (const item of results) {
    fragment.appendChild(buildCard(item));
  }
  resultsNode.appendChild(fragment);
}

async function handleSearch() {
  if (state.isLoading) {
    return;
  }
  await loadTopics();

  const query = searchInput.value.trim();
  const verify = verifyToggle.checked;
  const topic = topicFilter.value;

  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (topic) params.set("topic", topic);
  params.set("verify", verify ? "true" : "false");

  setBusy(true);
  setStatus("Loading evidence…");

  try {
    const results = await fetchJSON(`/api/search?${params.toString()}`);
    renderResults(results);
    const message = results.length === 1 ? "Showing 1 result" : `Showing ${results.length} results`;
    setStatus(message);
    state.lastQuery = query;
  } catch (error) {
    console.error("Search failed", error);
    renderResults([]);
    setStatus("Unable to load evidence. Please try again.", "error");
  } finally {
    setBusy(false);
  }
}

searchButton.addEventListener("click", () => {
  handleSearch();
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    handleSearch();
  }
});

verifyToggle.addEventListener("change", () => handleSearch());
topicFilter.addEventListener("change", () => handleSearch());

handleSearch();

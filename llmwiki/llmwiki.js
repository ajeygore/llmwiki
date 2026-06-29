/**
 * LLMWiki Engine Core
 * A minimal, zero-build client-side router & renderer for LLM-maintained wikis.
 * Supports dynamic tag indexing, directory grouping, and search with floating dropdowns.
 */

const DEFAULT_PAGE = 'wiki/index.md';
const SIDEBAR_SOURCE = 'wiki/index.md';
let currentPage = DEFAULT_PAGE;

// Global Master Index populated via background crawler
let masterIndex = {
  pages: [],
  tags: {},
  groups: {}
};

// Resolve relative path relative to a base file path
function resolveRelativePath(basePath, relativePath) {
  if (relativePath.match(/^(https?:|mailto:|tel:|#|\/\/)/)) {
    return relativePath;
  }
  
  const parts = basePath.split('/');
  parts.pop(); // remove file name to get directory
  
  const relParts = relativePath.split('/');
  for (const part of relParts) {
    if (part === '.' || part === '') {
      continue;
    } else if (part === '..') {
      parts.pop();
    } else {
      parts.push(part);
    }
  }
  
  return parts.join('/');
}

// Format file paths into human readable titles
function getPageTitle(path) {
  const filename = path.split('/').pop();
  const nameWithoutExt = filename.replace(/\.md$/, '');
  return nameWithoutExt
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Zero-dependency YAML Frontmatter Parser
function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, content: markdown };
  }
  
  const yamlText = match[1];
  const content = match[2];
  const frontmatter = {};
  
  const lines = yamlText.split('\n');
  lines.forEach(line => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.slice(0, colonIndex).trim();
      let value = line.slice(colonIndex + 1).trim();
      
      // Handle array format [a, b, c]
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map(v => v.trim().replace(/^['"]|['"]$/g, ''));
      } else if (value.startsWith('- ')) {
        // Standard list item in frontmatter (handled if simple)
        value = value.replace(/^- /, '').trim();
      } else {
        value = value.replace(/^['"]|['"]$/g, '');
      }
      
      // Accumulate arrays
      if (frontmatter[key]) {
        if (Array.isArray(frontmatter[key])) {
          frontmatter[key].push(value);
        } else {
          frontmatter[key] = [frontmatter[key], value];
        }
      } else {
        frontmatter[key] = value;
      }
    }
  });
  
  return { frontmatter, content };
}

// Load and render a markdown file
async function loadPage(pagePath) {
  const contentArea = document.getElementById('content');
  currentPage = pagePath;
  
  // Update raw markdown link
  const rawLink = document.getElementById('rawLink');
  rawLink.href = pagePath;

  // Update Breadcrumbs
  updateBreadcrumbs(pagePath);

  // If loading the main index page, we render the gorgeous dynamic explorer catalog!
  if (pagePath === 'wiki/index.md') {
    renderCatalogExplorer(contentArea);
    highlightActiveSidebarItem(pagePath);
    document.title = 'Explore Catalog | LLMWiki';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  try {
    const response = await fetch(pagePath);
    if (!response.ok) {
      throw new Error(`Failed to load page: ${response.statusText} (${response.status})`);
    }
    const markdown = await response.text();
    
    // Parse frontmatter & content
    const { frontmatter, content } = parseFrontmatter(markdown);
    
    // Parse Markdown to HTML
    let html = marked.parse(content);
    contentArea.innerHTML = html;
    
    // Add YAML Tags view at the bottom of the page if present
    if (frontmatter.tags) {
      const tagsList = Array.isArray(frontmatter.tags) ? frontmatter.tags : [frontmatter.tags];
      const tagsContainer = document.createElement('div');
      tagsContainer.style.marginTop = '2.5rem';
      tagsContainer.style.paddingTop = '1.5rem';
      tagsContainer.style.borderTop = '1px solid var(--border-color)';
      tagsContainer.innerHTML = `
        <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">Tags:</div>
        <div class="tag-list">
          ${tagsList.map(tag => `<a href="#/tag/${tag}" class="tag-badge">#${tag}</a>`).join('')}
        </div>
      `;
      contentArea.appendChild(tagsContainer);
    }
    
    // Post-process relative images and non-router links
    postProcessContent(contentArea, pagePath);
    
    // Apply Syntax Highlighting
    if (window.Prism) {
      Prism.highlightAllUnder(contentArea);
    }
    
    // Update active class in sidebar
    highlightActiveSidebarItem(pagePath);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Update document title
    const title = frontmatter.title || getPageTitle(pagePath);
    document.title = `${title} | LLMWiki`;
  } catch (error) {
    console.error(error);
    contentArea.innerHTML = `
      <div class="error-container">
        <div class="error-icon">📭</div>
        <h2>Page Not Found</h2>
        <p>Could not load the page: <code>${pagePath}</code></p>
        <p class="error-details">${error.message}</p>
        <a href="#/${DEFAULT_PAGE}" class="back-home-btn">Go to Catalog</a>
      </div>
    `;
    document.title = 'Page Not Found | LLMWiki';
  }
}

// Update the breadcrumb bar dynamically and link parent categories
function updateBreadcrumbs(pagePath) {
  const breadcrumb = document.getElementById('breadcrumb');
  if (!breadcrumb) return;
  
  breadcrumb.innerHTML = ''; // Clear all existing nodes to avoid duplicates
  
  const segments = pagePath.split('/');
  let currentPathAcc = '';
  
  segments.forEach((seg, index) => {
    if (index > 0) {
      const sep = document.createElement('span');
      sep.className = 'crumb-separator';
      sep.innerText = '/';
      breadcrumb.appendChild(sep);
    }
    
    const isLast = (index === segments.length - 1);
    const span = document.createElement('span');
    span.className = `crumb ${isLast ? 'active' : ''}`;
    
    // Format segment text nicely
    const displayName = seg.replace(/\.md$/, '');
    span.innerText = displayName;
    
    // Build the accumulator path
    if (index === 0) {
      currentPathAcc = seg;
    } else {
      currentPathAcc += '/' + seg;
    }
    
    if (!isLast) {
      span.style.cursor = 'pointer';
      // If segment is not a file, route to the index page of that subdirectory
      const targetPath = currentPathAcc.endsWith('.md') ? currentPathAcc : currentPathAcc + '/index.md';
      span.addEventListener('click', () => {
        window.location.hash = '#/' + targetPath;
      });
    } else {
      span.id = 'currentCrumb';
    }
    
    breadcrumb.appendChild(span);
  });
}

// Post-process content HTML to fix relative URLs and images
function postProcessContent(container, pagePath) {
  // Resolve image paths
  const images = container.querySelectorAll('img');
  images.forEach(img => {
    const src = img.getAttribute('src');
    if (src && !src.match(/^(https?:|\/\/|data:)/) && !src.startsWith('/')) {
      img.src = resolveRelativePath(pagePath, src);
    }
  });

  // Target blank for external links
  const links = container.querySelectorAll('a');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.match(/^(https?:|\/\/)/)) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });

  // Add floating copy code buttons to all code blocks
  const pres = container.querySelectorAll('pre');
  pres.forEach(pre => {
    if (pre.parentElement.classList.contains('code-block-wrapper')) {
      return;
    }
    
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.setAttribute('aria-label', 'Copy code to clipboard');
    copyBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="14" height="14" class="copy-icon">
        <path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
      </svg>
    `;
    
    copyBtn.addEventListener('click', async () => {
      const codeText = pre.querySelector('code')?.textContent || pre.textContent;
      try {
        await navigator.clipboard.writeText(codeText);
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = `
          <svg viewBox="0 0 24 24" width="14" height="14" class="tick-icon">
            <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        `;
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          copyBtn.innerHTML = `
            <svg viewBox="0 0 24 24" width="14" height="14" class="copy-icon">
              <path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
            </svg>
          `;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    });
    
    wrapper.appendChild(copyBtn);
  });
}

// Load the sidebar from wiki/index.md
async function loadSidebar() {
  const nav = document.getElementById('sidebarNav');
  try {
    const response = await fetch(SIDEBAR_SOURCE);
    if (!response.ok) {
      throw new Error('Could not load sidebar source index.md');
    }
    const markdown = await response.text();
    
    // Parse to HTML
    let html = marked.parse(markdown);
    nav.innerHTML = html;
    
    // Remove the main page title (H1) and intro paragraph from the sidebar
    const mainTitle = nav.querySelector('h1');
    if (mainTitle) mainTitle.remove();
    
    const paragraphs = nav.querySelectorAll('p');
    paragraphs.forEach(p => {
      if (!p.previousElementSibling || p.previousElementSibling.tagName === 'H1') {
        p.remove();
      }
    });
    
    // Post-process sidebar links to point to hash router
    const links = nav.querySelectorAll('a');
    links.forEach(link => {
      const href = link.getAttribute('href');
      if (href && !href.match(/^(https?:|\/\/|#)/)) {
        const resolved = resolveRelativePath(SIDEBAR_SOURCE, href);
        link.setAttribute('data-path', resolved);
        link.href = `#/${resolved}`;
      }
    });

    // Strip text descriptions next to links inside LI items in the sidebar
    const listItems = nav.querySelectorAll('li');
    listItems.forEach(li => {
      const link = li.querySelector('a');
      if (link) {
        li.innerHTML = '';
        li.appendChild(link);
      }
    });

    highlightActiveSidebarItem(currentPage);
  } catch (error) {
    console.error(error);
    nav.innerHTML = `
      <div class="sidebar-error">
        <p>Failed to load navigation index.</p>
        <p class="error-details">${error.message}</p>
      </div>
    `;
  }
}

// Highlight the active item in the sidebar
function highlightActiveSidebarItem(pagePath) {
  const nav = document.getElementById('sidebarNav');
  const links = nav.querySelectorAll('a');
  links.forEach(link => {
    const dataPath = link.getAttribute('data-path');
    if (dataPath === pagePath) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// Client Side Router
function handleRoute() {
  const hash = window.location.hash;
  
  if (hash.startsWith('#/tag/')) {
    const tagName = decodeURIComponent(hash.slice(6));
    renderTagView(tagName);
  } else if (hash.startsWith('#/group/')) {
    const groupName = decodeURIComponent(hash.slice(8));
    renderGroupView(groupName);
  } else {
    let targetPage = DEFAULT_PAGE;
    if (hash.startsWith('#/')) {
      targetPage = hash.slice(2);
    }
    loadPage(targetPage);
  }
  
  // Close mobile sidebar on route change
  document.body.classList.remove('sidebar-open');
}

// Search/Filter in Sidebar
function setupSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const nav = document.getElementById('sidebarNav');
    
    if (!query) {
      nav.querySelectorAll('*').forEach(el => el.style.display = '');
      return;
    }
    
    // Filter standard links
    const links = nav.querySelectorAll('a');
    links.forEach(link => {
      const text = link.textContent.toLowerCase();
      const match = text.includes(query);
      const li = link.closest('li');
      
      if (li) {
        li.style.display = match ? '' : 'none';
      } else {
        link.style.display = match ? '' : 'none';
      }
    });
    
    // Hide empty headers / lists
    const lists = nav.querySelectorAll('ul, ol');
    lists.forEach(list => {
      const visibleItems = Array.from(list.children).filter(child => child.style.display !== 'none');
      list.style.display = visibleItems.length > 0 ? '' : 'none';
      
      let prev = list.previousElementSibling;
      while (prev && prev.tagName.match(/^(H[1-6]|P)$/)) {
        prev.style.display = visibleItems.length > 0 ? '' : 'none';
        prev = prev.previousElementSibling;
      }
    });
  });
}

// Theme Toggle Functionality with System Preference Detection
function setupTheme() {
  const themeToggle = document.getElementById('themeToggle');
  const icon = themeToggle.querySelector('.mode-icon');
  const text = themeToggle.querySelector('.mode-text');
  
  let savedTheme = localStorage.getItem('theme');
  if (!savedTheme) {
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    savedTheme = prefersLight ? 'light' : 'dark';
  }
  
  const applyTheme = (theme) => {
    const themeLink = document.getElementById('prismThemeLink');
    if (theme === 'light') {
      document.body.classList.remove('dark-mode');
      document.body.classList.add('light-mode');
      icon.innerText = '🌙';
      text.innerText = 'Dark Mode';
      if (themeLink) {
        themeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css';
      }
    } else {
      document.body.classList.remove('light-mode');
      document.body.classList.add('dark-mode');
      icon.innerText = '☀';
      text.innerText = 'Light Mode';
      if (themeLink) {
        themeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css';
      }
    }
  };
  
  applyTheme(savedTheme);
  
  themeToggle.addEventListener('click', () => {
    if (document.body.classList.contains('dark-mode')) {
      applyTheme('light');
      localStorage.setItem('theme', 'light');
    } else {
      applyTheme('dark');
      localStorage.setItem('theme', 'dark');
    }
  });

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }
}

// Mobile sidebar responsiveness
function setupMobileNav() {
  const mobileToggleBtn = document.getElementById('mobileToggleBtn');
  const mobileCloseBtn = document.getElementById('mobileCloseBtn');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  
  mobileToggleBtn.addEventListener('click', () => {
    document.body.classList.add('sidebar-open');
  });
  
  const closeSidebar = () => {
    document.body.classList.remove('sidebar-open');
  };
  
  mobileCloseBtn.addEventListener('click', closeSidebar);
  sidebarOverlay.addEventListener('click', closeSidebar);
}

/* ==========================================================================
   LLMWiki Polish: Background Crawler and Tag/Group Indexing Engine
   ========================================================================== */

// Extract relative links pointing to markdown pages
function extractMdLinks(markdown) {
  const links = [];
  const regex = /\[([^\]]+)\]\(([^)]+\.md)\)/g;
  let match;
  while ((match = regex.exec(markdown)) !== null) {
    links.push({ text: match[1], path: match[2] });
  }
  return links;
}

// Background Crawler to index all workspace files, directory groups, and tags
async function crawlAndIndexWiki() {
  try {
    const response = await fetch(SIDEBAR_SOURCE);
    if (!response.ok) return;
    const markdown = await response.text();
    
    const links = extractMdLinks(markdown);
    
    // Clear previous index
    masterIndex = { pages: [], tags: {}, groups: {} };
    
    const fetchPromises = links.map(async (link) => {
      const resolvedPath = resolveRelativePath(SIDEBAR_SOURCE, link.path);
      try {
        const pageRes = await fetch(resolvedPath);
        if (!pageRes.ok) return;
        const pageText = await pageRes.text();
        
        const { frontmatter, content } = parseFrontmatter(pageText);
        
        // Extract Directory Group (folder structure)
        const segments = resolvedPath.split('/');
        let group = 'General';
        if (segments.length > 2) {
          // get the parent subdirectory name e.g. "wiki/engineering/page.md" -> "engineering"
          group = segments[segments.length - 2];
        }
        
        // Humanize group name
        const groupTitle = group.charAt(0).toUpperCase() + group.slice(1);
        
        // Extract tags
        let tagsList = [];
        if (frontmatter.tags) {
          tagsList = Array.isArray(frontmatter.tags) 
            ? frontmatter.tags 
            : [frontmatter.tags];
          tagsList = tagsList.map(t => t.trim().toLowerCase());
        }
        
        const pageTitle = frontmatter.title || link.text || getPageTitle(resolvedPath);
        const snippet = frontmatter.summary || content.replace(/[#*`]/g, '').slice(0, 140).trim() + '...';
        
        const pageData = {
          path: resolvedPath,
          title: pageTitle,
          group: groupTitle,
          tags: tagsList,
          summary: snippet
        };
        
        masterIndex.pages.push(pageData);
        
        // Populate Tags Index
        tagsList.forEach(tag => {
          if (!masterIndex.tags[tag]) {
            masterIndex.tags[tag] = [];
          }
          masterIndex.tags[tag].push(pageData);
        });
        
        // Populate Groups Index
        if (!masterIndex.groups[groupTitle]) {
          masterIndex.groups[groupTitle] = [];
        }
        masterIndex.groups[groupTitle].push(pageData);
        
      } catch (err) {
        console.warn(`Could not index page ${resolvedPath}:`, err);
      }
    });
    
    await Promise.all(fetchPromises);
    
    // Re-render sidebar navigation with dynamic elements (Groups and Tags)
    renderSidebarIndexes();
    
    // If we are currently looking at the catalog page, refresh the layout view
    if (currentPage === 'wiki/index.md') {
      renderCatalogExplorer(document.getElementById('content'));
    }
  } catch (err) {
    console.error('Failed to run crawl indexer:', err);
  }
}

// Render dynamic Groups and Tags menu lists at the bottom of the sidebar
function renderSidebarIndexes() {
  const nav = document.getElementById('sidebarNav');
  if (!nav) return;
  
  // Remove any previously appended dynamic sections
  const existingDividers = nav.querySelectorAll('.sidebar-section-divider, .dynamic-sidebar-heading, .dynamic-sidebar-list');
  existingDividers.forEach(el => el.remove());
  
  // Append Groups (directories) list if there are folders
  const groupsList = Object.keys(masterIndex.groups).sort();
  if (groupsList.length > 0) {
    const divider = document.createElement('hr');
    divider.className = 'sidebar-section-divider';
    nav.appendChild(divider);
    
    const heading = document.createElement('h2');
    heading.className = 'dynamic-sidebar-heading';
    heading.innerText = 'Directory Groups';
    nav.appendChild(heading);
    
    const ul = document.createElement('ul');
    ul.className = 'dynamic-sidebar-list';
    groupsList.forEach(groupName => {
      const pageCount = masterIndex.groups[groupName].length;
      const li = document.createElement('li');
      li.className = 'sidebar-list-item';
      li.innerHTML = `
        <a href="#/group/${encodeURIComponent(groupName)}" data-path="group/${groupName}">📁 ${groupName}</a>
        <span class="sidebar-count-indicator">${pageCount}</span>
      `;
      ul.appendChild(li);
    });
    nav.appendChild(ul);
  }
  
  // Append Tags list if there are tags
  const tagsList = Object.keys(masterIndex.tags).sort();
  if (tagsList.length > 0) {
    const divider = document.createElement('hr');
    divider.className = 'sidebar-section-divider';
    nav.appendChild(divider);
    
    const heading = document.createElement('h2');
    heading.className = 'dynamic-sidebar-heading';
    heading.innerText = 'Tags';
    nav.appendChild(heading);
    
    const ul = document.createElement('ul');
    ul.className = 'dynamic-sidebar-list';
    tagsList.forEach(tag => {
      const pageCount = masterIndex.tags[tag].length;
      const li = document.createElement('li');
      li.className = 'sidebar-list-item';
      li.innerHTML = `
        <a href="#/tag/${encodeURIComponent(tag)}" data-path="tag/${tag}">#${tag}</a>
        <span class="sidebar-count-indicator">${pageCount}</span>
      `;
      ul.appendChild(li);
    });
    nav.appendChild(ul);
  }
  
  // Re-highlight active item in sidebar (especially for dynamic groups/tags links)
  highlightActiveSidebarItem(window.location.hash.startsWith('#/') ? window.location.hash.slice(2) : currentPage);
}

// Render dynamic exploration dashboard inside the main index.md catalog panel
function renderCatalogExplorer(container) {
  if (!container) return;
  
  // Header section
  let html = `
    <h1 style="margin-top: 0;">Explore Catalog</h1>
    <p style="color: var(--text-secondary); margin-bottom: 2rem;">
      Welcome to your wiki catalog dashboard. All folder subdirectories are grouped below, with tags parsed dynamically from page metadata.
    </p>
  `;
  
  // 1. Directory Groups Folders Grid
  const groups = Object.keys(masterIndex.groups).sort();
  if (groups.length > 0) {
    html += `
      <div class="dashboard-section">
        <h2 class="dashboard-section-title">📁 Directories</h2>
        <div class="folder-grid">
          ${groups.map(groupName => {
            const count = masterIndex.groups[groupName].length;
            return `
              <a href="#/group/${encodeURIComponent(groupName)}" class="folder-card">
                <div class="folder-card-header">
                  <span class="folder-icon">📁</span>
                  <span class="folder-title">${groupName}</span>
                </div>
                <span class="folder-count">${count} ${count === 1 ? 'page' : 'pages'}</span>
              </a>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }
  
  // 2. Tags Badge list
  const tags = Object.keys(masterIndex.tags).sort();
  if (tags.length > 0) {
    html += `
      <div class="dashboard-section">
        <h2 class="dashboard-section-title">🏷️ Popular Tags</h2>
        <div class="tag-list" style="margin-top: 10px;">
          ${tags.map(tag => `
            <a href="#/tag/${encodeURIComponent(tag)}" class="tag-badge">#${tag} (${masterIndex.tags[tag].length})</a>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  // 3. Grid of All Pages
  if (masterIndex.pages.length > 0) {
    html += `
      <div class="dashboard-section">
        <h2 class="dashboard-section-title">📄 All Pages</h2>
        <div class="page-grid">
          ${masterIndex.pages.map(page => `
            <a href="#/${page.path}" class="page-card">
              <div class="page-card-header">
                <span class="page-card-title">${page.title}</span>
                <span class="group-badge">${page.group}</span>
              </div>
              <p class="page-card-summary">${page.summary}</p>
              ${page.tags.length > 0 ? `
                <div class="tag-list">
                  ${page.tags.map(tag => `<span class="tag-badge" style="pointer-events: none;">#${tag}</span>`).join('')}
                </div>
              ` : ''}
            </a>
          `).join('')}
        </div>
      </div>
    `;
  } else {
    html += `
      <div class="loading-placeholder">Building catalog directory indexes...</div>
    `;
  }
  
  container.innerHTML = html;
}

// Render dynamic Tag landing page listing matching cards
function renderTagView(tagName) {
  const container = document.getElementById('content');
  currentPage = `tag/${tagName}`;
  
  updateBreadcrumbs(`tags/${tagName}`);
  document.title = `Tag: #${tagName} | LLMWiki`;
  highlightActiveSidebarItem(`tag/${tagName}`);

  const matchingPages = masterIndex.tags[tagName.toLowerCase()] || [];
  
  let html = `
    <h1 style="margin-top: 0;">Tag: #${tagName}</h1>
    <p style="color: var(--text-secondary); margin-bottom: 2rem;">
      Found ${matchingPages.length} ${matchingPages.length === 1 ? 'page' : 'pages'} matching this tag.
    </p>
  `;
  
  if (matchingPages.length > 0) {
    html += `
      <div class="page-grid">
        ${matchingPages.map(page => `
          <a href="#/${page.path}" class="page-card">
            <div class="page-card-header">
              <span class="page-card-title">${page.title}</span>
              <span class="group-badge">${page.group}</span>
            </div>
            <p class="page-card-summary">${page.summary}</p>
            ${page.tags.length > 0 ? `
              <div class="tag-list">
                ${page.tags.map(t => `<span class="tag-badge" style="pointer-events: none;">#${t}</span>`).join('')}
              </div>
            ` : ''}
          </a>
        `).join('')}
      </div>
    `;
  } else {
    html += `
      <div class="error-container" style="max-width: 100%;">
        <div class="error-icon">🏷️</div>
        <h2>No Pages Found</h2>
        <p>There are no pages tagged with <code>#${tagName}</code>.</p>
        <a href="#/${DEFAULT_PAGE}" class="back-home-btn" style="margin-top: 16px;">Go to Catalog</a>
      </div>
    `;
  }
  
  container.innerHTML = html;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Render dynamic Directory Group landing page listing matching cards
function renderGroupView(groupName) {
  const container = document.getElementById('content');
  currentPage = `group/${groupName}`;
  
  updateBreadcrumbs(`groups/${groupName}`);
  document.title = `Group: ${groupName} | LLMWiki`;
  highlightActiveSidebarItem(`group/${groupName}`);

  const matchingPages = masterIndex.groups[groupName] || [];
  
  let html = `
    <h1 style="margin-top: 0;">Directory Group: ${groupName}</h1>
    <p style="color: var(--text-secondary); margin-bottom: 2rem;">
      Pages found inside the directory <code>/wiki/${groupName.toLowerCase()}</code>.
    </p>
  `;
  
  if (matchingPages.length > 0) {
    html += `
      <div class="page-grid">
        ${matchingPages.map(page => `
          <a href="#/${page.path}" class="page-card">
            <div class="page-card-header">
              <span class="page-card-title">${page.title}</span>
              <span class="group-badge">${page.group}</span>
            </div>
            <p class="page-card-summary">${page.summary}</p>
            ${page.tags.length > 0 ? `
              <div class="tag-list">
                ${page.tags.map(t => `<span class="tag-badge" style="pointer-events: none;">#${t}</span>`).join('')}
              </div>
            ` : ''}
          </a>
        `).join('')}
      </div>
    `;
  } else {
    html += `
      <div class="error-container" style="max-width: 100%;">
        <div class="error-icon">📁</div>
        <h2>Empty Folder</h2>
        <p>There are no pages listed inside the group folder <code>${groupName}</code>.</p>
        <a href="#/${DEFAULT_PAGE}" class="back-home-btn" style="margin-top: 16px;">Go to Catalog</a>
      </div>
    `;
  }
  
  container.innerHTML = html;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ==========================================================================
   LLMWiki Polish: Header Search Controller with Floating Dropdown
   ========================================================================== */

function setupHeaderSearch() {
  const searchInput = document.getElementById('globalSearchInput');
  const clearBtn = document.getElementById('clearSearchBtn');
  const dropdown = document.getElementById('searchDropdown');
  
  if (!searchInput || !dropdown) return;
  
  const showResults = (query) => {
    const q = query.toLowerCase().trim();
    if (!q) {
      dropdown.innerHTML = '';
      dropdown.style.display = 'none';
      clearBtn.style.display = 'none';
      return;
    }
    
    clearBtn.style.display = '';
    
    // Query filter matching title, tags, group, or summary
    const matches = masterIndex.pages.filter(page => {
      return page.title.toLowerCase().includes(q) || 
             page.group.toLowerCase().includes(q) || 
             page.summary.toLowerCase().includes(q) ||
             page.tags.some(tag => tag.toLowerCase().includes(q));
    });
    
    if (matches.length > 0) {
      dropdown.innerHTML = matches.map(page => `
        <a href="#/${page.path}" class="search-result-item">
          <div class="search-result-title">${page.title} <span class="group-badge" style="font-size: 0.6rem; padding: 1px 4px; vertical-align: middle;">${page.group}</span></div>
          <div class="search-result-snippet">${page.summary}</div>
        </a>
      `).join('');
    } else {
      dropdown.innerHTML = `<div class="search-no-results">No pages match "${query}"</div>`;
    }
    dropdown.style.display = 'block';
  };
  
  searchInput.addEventListener('input', (e) => {
    showResults(e.target.value);
  });
  
  searchInput.addEventListener('focus', (e) => {
    if (e.target.value) {
      showResults(e.target.value);
    }
  });
  
  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    showResults('');
    searchInput.focus();
  });
  
  // Close dropdown on click outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.header-search-container')) {
      dropdown.style.display = 'none';
    }
  });
  
  // Intercept click on results items to close dropdown
  dropdown.addEventListener('click', (e) => {
    if (e.target.closest('.search-result-item')) {
      dropdown.style.display = 'none';
      searchInput.value = '';
      clearBtn.style.display = 'none';
    }
  });
}

// App Initialization
document.addEventListener('DOMContentLoaded', async () => {
  setupTheme();
  setupMobileNav();
  
  // Load sidebar first to establish navigation
  await loadSidebar();
  
  // Setup search bar in sidebar header filter
  setupSearch();
  
  // Listen to hash changes
  window.addEventListener('hashchange', handleRoute);
  
  // Run initial route setup
  handleRoute();
  
  // Run background indexing crawler to discover pages, tags, and subfolders
  crawlAndIndexWiki();
  
  // Setup header search floating engine
  setupHeaderSearch();
  
  // Global click interceptor for relative markdown links
  document.addEventListener('click', (event) => {
    const target = event.target.closest('a');
    if (!target) return;
    
    const href = target.getAttribute('href');
    if (!href) return;
    
    if (href.startsWith('#') || href.match(/^(https?:|mailto:|tel:|\/\/)/)) {
      return;
    }
    
    if (href.endsWith('.md') || href.includes('.md#')) {
      event.preventDefault();
      const isSidebar = target.closest('#sidebarNav');
      const base = isSidebar ? SIDEBAR_SOURCE : currentPage;
      const resolved = resolveRelativePath(base, href);
      window.location.hash = `#/${resolved}`;
    }
  });
});

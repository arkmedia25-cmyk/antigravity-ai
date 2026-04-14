document_ready = () => {
    console.log("Antigravity Agency OS UI Initialized");
    
    // Static project data for the prototype
    const mockProjects = [
        { id: "PRJ-001", name: "Wellness Reels", brand: "@holisti", status: "Active", progress: 75 },
        { id: "PRJ-002", name: "Market Research - Aloe", brand: "@glowup", status: "Live", progress: 100 },
        { id: "PRJ-003", name: "Email Campaign", brand: "@holisti", status: "Active", progress: 30 },
        { id: "PRJ-004", name: "StikTok Ads", brand: "@glowup", status: "Draft", progress: 10 }
    ];

    const projectList = document.querySelector('.project-list');

    const renderProjects = (projects) => {
        projectList.innerHTML = '';
        projects.forEach(p => {
            const row = document.createElement('div');
            row.className = 'project-row';
            row.innerHTML = `
                <div class="p-id">${p.id}</div>
                <div class="p-name">${p.name}</div>
                <div class="p-brand">${p.brand}</div>
                <div class="p-status"><span class="badge ${p.status.toLowerCase()}">${p.status}</span></div>
                <div class="p-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${p.progress}%"></div>
                    </div>
                    <span>${p.progress}%</span>
                </div>
            `;
            projectList.appendChild(row);
        });
    };

    renderProjects(mockProjects);

    // AI Orb Listener
    const aiOrb = document.querySelector('.ai-orb');
    aiOrb.addEventListener('click', () => {
        alert("AI Assistant Chat Opening... (Connecting to Swarm Orchestrator)");
    });

    // Sidebar interaction
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
};

document.addEventListener('DOMContentLoaded', document_ready);

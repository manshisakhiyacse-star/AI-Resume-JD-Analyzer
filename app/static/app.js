document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const tabFile = document.getElementById('tab-file');
    const tabText = document.getElementById('tab-text');
    const contentFile = document.getElementById('content-file');
    const contentText = document.getElementById('content-text');
    
    const dropZone = document.getElementById('drop-zone');
    const resumeFileInput = document.getElementById('resume-file');
    const browseBtn = document.getElementById('browse-btn');
    const fileInfo = document.getElementById('file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const uploadPrompt = document.querySelector('.upload-prompt');
    
    const resumeText = document.getElementById('resume-text');
    const jobDescription = document.getElementById('job-description');
    const resumeTextCounter = document.getElementById('resume-text-counter');
    const jdCounter = document.getElementById('jd-counter');
    
    const form = document.getElementById('analyze-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnIcon = submitBtn.querySelector('.btn-icon');
    const spinner = submitBtn.querySelector('.spinner');
    
    const resultsPanel = document.getElementById('results-panel');
    const resultsEmptyState = document.getElementById('results-empty-state');
    const resultsContent = document.getElementById('results-content');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    const overallScoreDisplay = document.getElementById('overall-score-display');
    const overallRing = document.getElementById('overall-ring');
    const resAnalysisId = document.getElementById('res-analysis-id');
    const skillScoreVal = document.getElementById('skill-score-val');
    const skillScoreBar = document.getElementById('skill-score-bar');
    const semanticScoreVal = document.getElementById('semantic-score-val');
    const semanticScoreBar = document.getElementById('semantic-score-bar');
    
    const listMatchedSkills = document.getElementById('list-matched-skills');
    const listMissingSkills = document.getElementById('list-missing-skills');
    const listAdditionalSkills = document.getElementById('list-additional-skills');
    
    const badgeCountMatched = document.getElementById('badge-count-matched');
    const badgeCountMissing = document.getElementById('badge-count-missing');
    
    const recommendationsList = document.getElementById('recommendations-list');
    
    const accordionToggle = document.getElementById('accordion-toggle');
    const accordionContent = document.getElementById('accordion-content');
    const explainableTableBody = document.getElementById('explainable-table-body');
    
    const toastContainer = document.getElementById('toast-container');

    let selectedFile = null;
    let activeTab = 'file'; // 'file' or 'text'

    // Tab Switching Logic
    tabFile.addEventListener('click', () => {
        activeTab = 'file';
        tabFile.classList.add('active');
        tabText.classList.remove('active');
        contentFile.classList.add('active');
        contentText.classList.remove('active');
    });

    tabText.addEventListener('click', () => {
        activeTab = 'text';
        tabText.classList.add('active');
        tabFile.classList.remove('active');
        contentText.classList.add('active');
        contentFile.classList.remove('active');
    });

    // File Drag & Drop Handlers
    browseBtn.addEventListener('click', () => resumeFileInput.click());
    
    resumeFileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file) return;
        
        // Simple client-side size check (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            showToast("File size exceeds the 10MB limit.");
            return;
        }
        
        selectedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        
        uploadPrompt.style.display = 'none';
        fileInfo.style.display = 'flex';
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        resumeFileInput.value = '';
        fileInfo.style.display = 'none';
        uploadPrompt.style.display = 'block';
    });

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Character Counters
    resumeText.addEventListener('input', () => {
        const len = resumeText.value.length;
        resumeTextCounter.textContent = `${len.toLocaleString()} / 50,000`;
        if (len > 50000) {
            resumeTextCounter.style.color = '#ef4444';
        } else {
            resumeTextCounter.style.color = '';
        }
    });

    jobDescription.addEventListener('input', () => {
        const len = jobDescription.value.length;
        jdCounter.textContent = `${len.toLocaleString()} / 50,000`;
        if (len > 50000) {
            jdCounter.style.color = '#ef4444';
        } else {
            jdCounter.style.color = '';
        }
    });

    // Form Submission & Analysis API Call
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const jdVal = jobDescription.value.trim();
        if (!jdVal) {
            showToast("Job description is required.");
            return;
        }
        
        if (activeTab === 'file' && !selectedFile) {
            showToast("Please upload a resume file.");
            return;
        }
        
        if (activeTab === 'text' && !resumeText.value.trim()) {
            showToast("Please paste resume text.");
            return;
        }

        // Toggle Loading UI
        setLoadingState(true);
        
        try {
            let response;
            let data;
            
            if (activeTab === 'file') {
                const formData = new FormData();
                formData.append('resume_file', selectedFile);
                formData.append('job_description', jdVal);
                
                response = await fetch('/api/v1/analyze', {
                    method: 'POST',
                    body: formData
                });
            } else {
                const payload = {
                    resume_text: resumeText.value.trim(),
                    job_description: jdVal
                };
                
                response = await fetch('/api/v1/analyze/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
            }
            
            data = await response.json();
            
            if (!response.ok) {
                let errorMsg = "An unexpected error occurred during processing.";
                if (data && data.error && data.error.message) {
                    errorMsg = data.error.message;
                } else if (data && data.detail) {
                    errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
                }
                throw new Error(errorMsg);
            }
            
            // Success! Render data
            renderResults(data);
            
        } catch (error) {
            showToast(error.message);
            resultsEmptyState.style.display = 'flex';
            resultsContent.style.display = 'none';
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnIcon.style.display = 'none';
            spinner.style.display = 'inline-block';
            
            resultsEmptyState.style.display = 'none';
            resultsContent.style.display = 'none';
            loadingOverlay.style.display = 'flex';
        } else {
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnIcon.style.display = 'inline';
            spinner.style.display = 'none';
            
            loadingOverlay.style.display = 'none';
        }
    }

    // Render Results Logic
    function renderResults(data) {
        resultsEmptyState.style.display = 'none';
        resultsContent.style.display = 'block';
        
        // 1. Overall Score Circular Animation
        const score = Math.round(data.overall_score);
        overallScoreDisplay.textContent = score;
        
        // Circular ring calculation (circumference = 2 * PI * r = 2 * 3.14159 * 70 ≈ 440)
        const circumference = 440;
        const offset = circumference - (score / 100) * circumference;
        overallRing.style.strokeDashoffset = offset;
        
        // Color overall ring dynamically based on score
        if (score >= 75) {
            overallRing.style.stroke = 'var(--color-success)';
        } else if (score >= 50) {
            overallRing.style.stroke = 'var(--color-warning)';
        } else {
            overallRing.style.stroke = 'var(--color-danger)';
        }
        
        // Meta
        resAnalysisId.textContent = data.analysis_id;
        
        // 2. Skill & Semantic Scores
        const skillScore = Math.round(data.skill_match_score);
        skillScoreVal.textContent = `${skillScore}%`;
        skillScoreBar.style.width = `${skillScore}%`;
        
        const semanticScore = Math.round(data.semantic_similarity_score);
        semanticScoreVal.textContent = `${semanticScore}%`;
        semanticScoreBar.style.width = `${semanticScore}%`;
        
        // 3. Render Skill Pills
        listMatchedSkills.innerHTML = '';
        if (data.matched_skills && data.matched_skills.length > 0) {
            badgeCountMatched.textContent = data.matched_skills.length;
            data.matched_skills.forEach(skill => {
                const el = document.createElement('span');
                el.className = 'skill-tag tag-matched';
                el.innerHTML = `<i class="fa-solid fa-check"></i> ${escapeHtml(skill)}`;
                listMatchedSkills.appendChild(el);
            });
        } else {
            badgeCountMatched.textContent = '0';
            listMatchedSkills.innerHTML = '<span class="text-muted" style="font-size:0.8rem; padding:0.5rem 0;">No matching skills identified.</span>';
        }
        
        listMissingSkills.innerHTML = '';
        if (data.missing_skills && data.missing_skills.length > 0) {
            badgeCountMissing.textContent = data.missing_skills.length;
            data.missing_skills.forEach(skill => {
                const el = document.createElement('span');
                el.className = 'skill-tag tag-missing';
                el.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(skill)}`;
                listMissingSkills.appendChild(el);
            });
        } else {
            badgeCountMissing.textContent = '0';
            listMissingSkills.innerHTML = '<span class="text-muted" style="font-size:0.8rem; padding:0.5rem 0;">No missing skills gaps.</span>';
        }
        
        listAdditionalSkills.innerHTML = '';
        if (data.additional_skills && data.additional_skills.length > 0) {
            data.additional_skills.forEach(skill => {
                const el = document.createElement('span');
                el.className = 'skill-tag tag-additional';
                el.innerHTML = `<i class="fa-solid fa-plus"></i> ${escapeHtml(skill)}`;
                listAdditionalSkills.appendChild(el);
            });
        } else {
            listAdditionalSkills.innerHTML = '<span class="text-muted" style="font-size:0.8rem; padding:0.5rem 0;">No additional skills detected.</span>';
        }
        
        // 4. Render Actionable Recommendations
        recommendationsList.innerHTML = '';
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const el = document.createElement('li');
                el.className = 'recommendation-item';
                el.innerHTML = `
                    <i class="fa-solid fa-lightbulb rec-bullet"></i>
                    <span class="rec-text">${escapeHtml(rec)}</span>
                `;
                recommendationsList.appendChild(el);
            });
        } else {
            recommendationsList.innerHTML = '<li class="text-muted" style="font-size:0.85rem; padding:0.5rem 0;">Candidate perfectly aligns with job requirements. No recommendations needed.</li>';
        }
        
        // 5. Populate Explainable Mapping Table & Summary Cards
        explainableTableBody.innerHTML = '';
        const explainMap = data.explainable_matches || {};
        const jobRequired = data.job_required_skills || [];
        
        let exactCount = 0;
        let semanticCount = 0;
        let gapCount = 0;
        
        if (jobRequired.length > 0) {
            jobRequired.forEach(reqSkill => {
                const tr = document.createElement('tr');
                const matchInfo = explainMap[reqSkill];
                
                if (matchInfo) {
                    const similarity = Math.round(matchInfo.similarity_score);
                    const typeClass = matchInfo.match_type === 'exact' ? 'badge-exact' : 'badge-semantic';
                    if (matchInfo.match_type === 'exact') {
                        exactCount++;
                    } else {
                        semanticCount++;
                    }
                    tr.innerHTML = `
                        <td><strong>${escapeHtml(reqSkill)}</strong></td>
                        <td>${escapeHtml(matchInfo.matched_to_resume_skill)}</td>
                        <td><span class="score-badge ${typeClass}">${similarity}%</span></td>
                        <td><span class="score-badge ${typeClass}">${escapeHtml(matchInfo.match_type)}</span></td>
                    `;
                } else {
                    // Not matched (Gap)
                    gapCount++;
                    tr.innerHTML = `
                        <td><strong>${escapeHtml(reqSkill)}</strong></td>
                        <td><span class="text-muted">None</span></td>
                        <td><span class="score-badge badge-missing">0%</span></td>
                        <td><span class="score-badge badge-missing">unmatched</span></td>
                    `;
                }
                explainableTableBody.appendChild(tr);
            });
        } else {
            explainableTableBody.innerHTML = '<tr><td colspan="4" class="text-muted" style="text-align:center;">No required skills identified in job description to compile matching table.</td></tr>';
        }
        
        // Update summary cards
        document.getElementById('summary-exact-count').textContent = exactCount;
        document.getElementById('summary-semantic-count').textContent = semanticCount;
        document.getElementById('summary-gap-count').textContent = gapCount;
        
        // Generate semantic gap explanation text
        const semanticExplanationText = document.getElementById('semantic-explanation-text');
        let explanationText = "";
        const totalReq = jobRequired.length;
        
        if (totalReq === 0) {
            explanationText = "No required skills identified in the job description to generate semantic alignment metrics.";
        } else {
            const semanticScore = Math.round(data.semantic_similarity_score);
            explanationText = `The candidate matches <span class="text-highlight-green">${exactCount}</span> required skills exactly and <span class="text-highlight-indigo">${semanticCount}</span> skills semantically. There are <span class="text-highlight-red">${gapCount}</span> skill gaps remaining.<br><br>`;
            
            if (gapCount === 0) {
                explanationText += `The candidate's profile is fully covered! No direct keyword gaps exist. The overall semantic similarity score of <span class="text-highlight-green">${semanticScore}%</span> suggests an excellent contextual alignment with the role's domain.`;
            } else {
                const missingList = data.missing_skills && data.missing_skills.length > 0 ? data.missing_skills.join(", ") : "None";
                explanationText += `<strong>Key Gaps & Missing Keywords:</strong> to improve the candidate's compatibility and raise the overall similarity score (currently <span class="text-highlight-indigo">${semanticScore}%</span>), it is highly recommended to clarify experience or add context around the missing key points: <span class="text-highlight-red">${escapeHtml(missingList)}</span>.`;
            }
        }
        semanticExplanationText.innerHTML = explanationText;
    }

    // Accordion Toggle
    accordionToggle.addEventListener('click', () => {
        accordionToggle.classList.toggle('active');
        accordionContent.classList.toggle('open');
    });

    // Toast Notifications
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>${escapeHtml(message)}</span>
        `;
        toastContainer.appendChild(toast);
        
        // Auto remove toast
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
});

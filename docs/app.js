/**
 * PyDataShred Documentation Portal - Interactive Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  initSearch();
  initCopyButtons();
  initTabs();
  initScrollSpy();
  initGovernanceSimulator();
  initCodeGenerator();
  initApiExplorer();
  initThemeToggle();
  initMobileMenu();
});

/* --------------------------------------------------------------------------
   1. Search Engine
   -------------------------------------------------------------------------- */
function initSearch() {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  if (!searchInput || !searchResults) return;

  // Build index from headers and sections
  const sections = Array.from(document.querySelectorAll('.doc-section, .feature-card, .tab-content, .hero-banner'));
  const searchIndex = [];

  sections.forEach(sec => {
    const id = sec.id || sec.closest('.doc-section')?.id;
    const titleElem = sec.querySelector('h1, h2, h3, h4, .section-title, .feature-title');
    const title = titleElem ? titleElem.innerText.trim() : '';
    const text = sec.innerText.slice(0, 500).replace(/\s+/g, ' ').trim();
    
    if (title && id) {
      searchIndex.push({ id, title, text });
    }
  });

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      searchResults.style.display = 'none';
      searchResults.innerHTML = '';
      return;
    }

    const matches = searchIndex.filter(item => 
      item.title.toLowerCase().includes(query) || 
      item.text.toLowerCase().includes(query)
    ).slice(0, 8);

    if (matches.length === 0) {
      searchResults.innerHTML = `
        <div class="search-result-item" style="color: var(--text-muted); cursor: default;">
          No matching documentation found for "${escapeHtml(query)}"
        </div>`;
    } else {
      searchResults.innerHTML = matches.map(match => {
        const snippetIndex = match.text.toLowerCase().indexOf(query);
        let snippet = match.text;
        if (snippetIndex !== -1) {
          const start = Math.max(0, snippetIndex - 30);
          const end = Math.min(match.text.length, snippetIndex + 80);
          snippet = (start > 0 ? '...' : '') + match.text.slice(start, end) + (end < match.text.length ? '...' : '');
        } else {
          snippet = snippet.slice(0, 100) + '...';
        }

        return `
          <div class="search-result-item" data-target="${match.id}">
            <div class="search-result-title">${escapeHtml(match.title)}</div>
            <div class="search-result-snippet">${highlightKeyword(snippet, query)}</div>
          </div>`;
      }).join('');
    }

    searchResults.style.display = 'block';
  });

  searchResults.addEventListener('click', (e) => {
    const item = e.target.closest('.search-result-item');
    if (!item) return;
    const targetId = item.getAttribute('data-target');
    if (targetId) {
      const targetElem = document.getElementById(targetId);
      if (targetElem) {
        targetElem.scrollIntoView({ behavior: 'smooth' });
        searchResults.style.display = 'none';
        searchInput.value = '';
      }
    }
  });

  // Keyboard shortcut Ctrl+K / Cmd+K
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape') {
      searchResults.style.display = 'none';
    }
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = 'none';
    }
  });
}

function highlightKeyword(text, keyword) {
  const regex = new RegExp(`(${escapeRegex(keyword)})`, 'gi');
  return escapeHtml(text).replace(regex, '<span style="color: var(--cyan-primary); font-weight: 700; background: rgba(6, 182, 212, 0.15); padding: 0 2px; border-radius: 2px;">$1</span>');
}

function escapeHtml(string) {
  return String(string)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/* --------------------------------------------------------------------------
   2. Copy Code to Clipboard
   -------------------------------------------------------------------------- */
function initCopyButtons() {
  document.querySelectorAll('.copy-code-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const container = btn.closest('.code-container');
      const codeElem = container.querySelector('code, pre');
      if (!codeElem) return;

      const codeText = codeElem.innerText;
      navigator.clipboard.writeText(codeText).then(() => {
        const originalText = btn.innerHTML;
        btn.classList.add('copied');
        btn.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>
          Copied!
        `;
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = originalText;
        }, 2000);
      });
    });
  });
}

/* --------------------------------------------------------------------------
   3. Tabs Component
   -------------------------------------------------------------------------- */
function initTabs() {
  document.querySelectorAll('.tab-container').forEach(container => {
    const btns = container.querySelectorAll('.tab-btn');
    const contents = container.querySelectorAll('.tab-content');

    btns.forEach((btn, idx) => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        if (contents[idx]) {
          contents[idx].classList.add('active');
        }
      });
    });
  });
}

/* --------------------------------------------------------------------------
   4. ScrollSpy & Sidebar Active Links
   -------------------------------------------------------------------------- */
function initScrollSpy() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = Array.from(document.querySelectorAll('.doc-section'));

  window.addEventListener('scroll', () => {
    let currentId = '';
    const scrollPos = window.scrollY + 120;

    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        currentId = section.id;
      }
    });

    if (currentId) {
      navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentId}`) {
          link.classList.add('active');
        }
      });
    }
  });
}

/* --------------------------------------------------------------------------
   5. Interactive Governance & Quality Simulator
   -------------------------------------------------------------------------- */
function initGovernanceSimulator() {
  const runBtn = document.getElementById('btn-run-sim');
  const outputBox = document.getElementById('sim-output');
  if (!runBtn || !outputBox) return;

  runBtn.addEventListener('click', () => {
    outputBox.innerHTML = '<span style="color: var(--cyan-primary);">Evaluating DataMesh Governance & Quality Rules...</span>';

    try {
      const schemaType = document.getElementById('sim-compliance-select')?.value || 'PUBLIC';
      const recordText = document.getElementById('sim-record-json')?.value || '{}';
      const retentionDays = parseInt(document.getElementById('sim-retention-input')?.value || '90', 10);
      const isPiiMarked = document.getElementById('sim-pii-marked')?.checked || false;

      const record = JSON.parse(recordText);

      // Simulation Logic
      setTimeout(() => {
        const evaluations = [];
        let overallDecision = 'ALLOW';
        const violations = [];
        const remediations = [];

        // 1. PII Detection Policy
        const piiFields = ['email', 'phone', 'ssn', 'credit_card', 'customer_id'];
        const detectedPii = Object.keys(record).filter(k => piiFields.some(p => k.toLowerCase().includes(p)));

        if (detectedPii.length > 0) {
          if (!isPiiMarked) {
            overallDecision = 'DENY';
            violations.push(`PII fields detected (${detectedPii.join(', ')}) but not declared in contract.pii_fields.`);
            remediations.push(`Update contract.pii_fields to include: [${detectedPii.map(p => `"${p}"`).join(', ')}]`);
          }
          if (schemaType === 'PUBLIC') {
            overallDecision = 'DENY';
            violations.push(`PII data found in a dataset classified with PUBLIC compliance level.`);
            remediations.push(`Elevate compliance_level to CONFIDENTIAL or RESTRICTED for PII datasets.`);
          }
        }

        evaluations.push({
          policy: 'PIIDetectionPolicy',
          decision: detectedPii.length > 0 && (!isPiiMarked || schemaType === 'PUBLIC') ? 'DENY' : 'ALLOW',
          message: detectedPii.length > 0 
            ? `Detected potential PII columns: ${detectedPii.join(', ')}` 
            : 'No undeclared PII fields detected.'
        });

        // 2. Data Retention Policy
        const retentionLimits = {
          'PUBLIC': 30,
          'INTERNAL': 90,
          'CONFIDENTIAL': 365,
          'RESTRICTED': 0 // requires custom approval
        };

        const maxAllowed = retentionLimits[schemaType] || 90;
        if (schemaType === 'RESTRICTED') {
          if (overallDecision !== 'DENY') overallDecision = 'REQUIRE_APPROVAL';
          evaluations.push({
            policy: 'DataRetentionPolicy',
            decision: 'REQUIRE_APPROVAL',
            message: 'RESTRICTED compliance requires Data Governance Board sign-off.'
          });
        } else if (retentionDays > maxAllowed) {
          if (overallDecision !== 'DENY') overallDecision = 'WARN';
          violations.push(`Retention period (${retentionDays} days) exceeds ${schemaType} limit of ${maxAllowed} days.`);
          remediations.push(`Lower retention_days to ${maxAllowed} days or request exception.`);
          evaluations.push({
            policy: 'DataRetentionPolicy',
            decision: 'WARN',
            message: `Retention ${retentionDays}d > max ${maxAllowed}d`
          });
        } else {
          evaluations.push({
            policy: 'DataRetentionPolicy',
            decision: 'ALLOW',
            message: `Retention ${retentionDays}d is within ${schemaType} limit (${maxAllowed}d).`
          });
        }

        // 3. Null Threshold Policy & Constraint Validation
        let nullCount = 0;
        let totalFields = 0;
        for (const [key, val] of Object.entries(record)) {
          totalFields++;
          if (val === null || val === undefined || val === '') {
            nullCount++;
          }
        }

        const nullRate = totalFields > 0 ? (nullCount / totalFields) : 0;
        if (nullRate > 0.3) {
          if (overallDecision !== 'DENY') overallDecision = 'WARN';
          violations.push(`Null rate ${(nullRate * 100).toFixed(1)}% exceeds standard threshold (10%).`);
          evaluations.push({
            policy: 'NullThresholdPolicy',
            decision: 'WARN',
            message: `Null rate ${(nullRate * 100).toFixed(1)}% is elevated.`
          });
        } else {
          evaluations.push({
            policy: 'NullThresholdPolicy',
            decision: 'ALLOW',
            message: `Null values within threshold (${(nullRate * 100).toFixed(1)}%).`
          });
        }

        // Render Output
        const badgeClass = overallDecision === 'ALLOW' ? 'pass' : (overallDecision === 'DENY' ? 'deny' : 'warn');
        let html = `
          <div style="margin-bottom: 1rem;">
            <span class="sim-badge ${badgeClass}">${overallDecision}</span>
            <strong style="color: #fff; font-size: 1rem;">Overall Evaluation Result</strong>
          </div>
          <div style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 0.8rem;">
            Timestamp: ${new Date().toISOString()} | Engine: GovernanceEngine v2.0
          </div>
          <div style="margin-bottom: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.8rem;">
            <strong style="color: var(--cyan-primary);">Policy Breakdown:</strong>
        `;

        evaluations.forEach(ev => {
          const evBadge = ev.decision === 'ALLOW' ? 'pass' : (ev.decision === 'DENY' ? 'deny' : 'warn');
          html += `
            <div style="margin-top: 0.4rem; padding-left: 0.5rem; border-left: 2px solid ${ev.decision === 'ALLOW' ? 'var(--emerald-primary)' : 'var(--rose-primary)'}">
              <span class="sim-badge ${evBadge}">${ev.decision}</span>
              <strong>${ev.policy}</strong>: ${escapeHtml(ev.message)}
            </div>
          `;
        });

        if (violations.length > 0) {
          html += `
            <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(244, 63, 94, 0.1); border-radius: 6px; border: 1px solid rgba(244, 63, 94, 0.3);">
              <strong style="color: var(--rose-primary);">Violations Detected (${violations.length}):</strong>
              <ul style="margin: 0.4rem 0 0 1.2rem; color: #fecdd3;">
                ${violations.map(v => `<li>${escapeHtml(v)}</li>`).join('')}
              </ul>
            </div>
          `;
        }

        if (remediations.length > 0) {
          html += `
            <div style="margin-top: 0.8rem; padding: 0.8rem; background: rgba(6, 182, 212, 0.1); border-radius: 6px; border: 1px solid rgba(6, 182, 212, 0.3);">
              <strong style="color: var(--cyan-primary);">Recommended Remediations:</strong>
              <ul style="margin: 0.4rem 0 0 1.2rem; color: #cffafe;">
                ${remediations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          `;
        }

        html += '</div>';
        outputBox.innerHTML = html;
      }, 300);

    } catch (err) {
      outputBox.innerHTML = `<span style="color: var(--rose-primary);">Error parsing sample JSON: ${escapeHtml(err.message)}</span>`;
    }
  });
}

/* --------------------------------------------------------------------------
   6. Interactive Pipeline Code Generator
   -------------------------------------------------------------------------- */
function initCodeGenerator() {
  const genBtn = document.getElementById('btn-gen-code');
  const codeOutput = document.getElementById('gen-code-output');
  if (!genBtn || !codeOutput) return;

  function generateCode() {
    const sourceFormat = document.getElementById('gen-source-format')?.value || 'CSV';
    const engine = document.getElementById('gen-engine')?.value || 'PySpark';
    const useScd2 = document.getElementById('gen-scd2')?.checked || false;
    const keyCol = document.getElementById('gen-key-col')?.value || 'transaction_id';
    const useMesh = document.getElementById('gen-mesh')?.checked || false;
    const targetSystem = document.getElementById('gen-target')?.value || 'Snowflake';

    let code = `"""
PyDataShred Auto-Generated Pipeline
Generated via PyDataShred Studio
"""
import logging
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType, DbType
`;

    if (useScd2) {
      code += `from datashredpy.helper.transform import ETL\n`;
    }

    if (engine === 'PySpark') {
      code += `from datashredpy.utilities.init_spark import SparkSessionOption\n`;
    }

    if (useMesh) {
      code += `from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel,
    DataProductPipeline
)
from datashredpy.api.models import Domain, App, Resources
`;
    }

    code += `\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger("DataPipeline")\n\ndef run_pipeline():\n`;

    if (engine === 'PySpark') {
      code += `    # 1. Initialize PySpark Session\n`;
      if (targetSystem === 'Snowflake' || sourceFormat === 'Snowflake') {
        code += `    spark = SparkSessionOption.get_spark_instance(app_name="DataShred_Job", snow_spark=True)\n`;
      } else {
        code += `    spark = SparkSessionOption.get_spark_instance(app_name="DataShred_Job")\n`;
      }
      code += `    logger.info("Spark session ready.")\n\n`;
    }

    code += `    # 2. Ingest Source Data\n`;
    const usePandasParam = engine === 'Pandas' ? 'use_pandas=True, use_spark=False' : 'use_pandas=False, use_spark=True';
    const fileTypeMap = {
      'CSV': 'FileType.CSV',
      'JSON': 'FileType.JSON',
      'PARQUET': 'FileType.PARQUET',
      'DELTA': 'FileType.DELTA',
      'EXCEL': 'FileType.EXCEL',
      'XML': 'FileType.XML',
      'SNOWFLAKE': 'FileType.SNOWFLAKE'
    };
    const mappedType = fileTypeMap[sourceFormat] || 'FileType.CSV';

    if (sourceFormat === 'SNOWFLAKE') {
      code += `    df_source = Data.read(\n        "ANALYTICS.TRANSACTIONS",\n        file_type=${mappedType},\n        snowpark_options={"account": "my_org", "user": "ADMIN"}\n    )\n`;
    } else {
      code += `    df_source = Data.read(\n        "data/inbound_feed.${sourceFormat.toLowerCase()}",\n        file_type=${mappedType},\n        ${usePandasParam}\n    )\n`;
    }

    if (useScd2) {
      code += `\n    # 3. Apply Slowly Changing Dimensions (SCD Type 2)\n`;
      code += `    # In production, df_target is loaded from current warehouse table\n`;
      code += `    df_existing_target = Data.read("data/warehouse_snapshot.parquet", file_type=FileType.PARQUET, ${usePandasParam})\n`;
      code += `    scd_engine = ETL(source_df=df_source, target_df=df_existing_target, key_columns="${keyCol}")\n`;
      code += `    df_transformed = scd_engine.apply_scd2()\n`;
      code += `    logger.info("SCD2 applied: audit flags updated.")\n`;
    } else {
      code += `\n    # 3. Transformations\n`;
      code += `    df_transformed = df_source  # Apply business logic here\n`;
    }

    if (useMesh) {
      code += `\n    # 4. DataMesh Governance & Contract Enforcement\n`;
      code += `    contract = DataProductContract(\n`;
      code += `        contract_id="contract-v1.0.0",\n`;
      code += `        product_id="prod-${keyCol}",\n`;
      code += `        schema=Schema(version="1.0.0", fields=[\n`;
      code += `            SchemaField(name="${keyCol}", data_type=DataType.STRING, nullable=False),\n`;
      code += `            SchemaField(name="amount", data_type=DataType.DECIMAL, nullable=False, constraints={"min": 0})\n`;
      code += `        ]),\n`;
      code += `        quality_rules=[\n`;
      code += `            DataQualityRule(rule_id="q1", name="No Null Key", rule_type="null_check", applies_to=["${keyCol}"], threshold=1.0)\n`;
      code += `        ],\n`;
      code += `        sla=SLA(freshness_hours=24, availability_percent=99.9),\n`;
      code += `        compliance_level=ComplianceLevel.CONFIDENTIAL,\n`;
      code += `        retention_days=365\n`;
      code += `    )\n\n`;
      code += `    product = DataProduct(\n`;
      code += `        product_id="prod-${keyCol}",\n`;
      code += `        product_name="Enterprise Data Feed",\n`;
      code += `        description="Automated Ingestion Feed",\n`;
      code += `        owner_email="data-eng@company.com",\n`;
      code += `        domain=Domain(domain_name="CoreOperations"),\n`;
      code += `        app=App(app_id=1, app_name="PipelineEngine", resources=Resources(source=None, target=None)),\n`;
      code += `        contract=contract\n`;
      code += `    )\n\n`;
      code += `    pipeline = DataProductPipeline(product, contract)\n`;
      code += `    # Execute governed phases\n`;
      code += `    ingest_check = pipeline.ingestion_phase(df_source, source_name="${sourceFormat}")\n`;
      code += `    transform_check = pipeline.transformation_phase(df_transformed)\n`;
      code += `    publish_result = pipeline.publication_phase(transform_check["output_df"], target_name="${targetSystem}")\n\n`;
      code += `    if publish_result["passed"]:\n`;
      code += `        logger.info(f"Pipeline successfully published to ${targetSystem}!")\n`;
      code += `    else:\n`;
      code += `        logger.error(f"Governance or Quality check failed: {publish_result}")\n`;
    } else {
      code += `\n    # 4. Publication\n`;
      code += `    logger.info(f"Writing payload to ${targetSystem}...")\n`;
      code += `    # Target write operation\n`;
    }

    code += `\nif __name__ == "__main__":\n    run_pipeline()\n`;

    codeOutput.textContent = code;
  }

  genBtn.addEventListener('click', generateCode);
  generateCode(); // Initial run
}

/* --------------------------------------------------------------------------
   7. REST API Mock Explorer
   -------------------------------------------------------------------------- */
function initApiExplorer() {
  const sendBtn = document.getElementById('btn-api-send');
  const apiEndpoint = document.getElementById('api-endpoint-select');
  const apiResponse = document.getElementById('api-response-output');
  if (!sendBtn || !apiEndpoint || !apiResponse) return;

  const mockEndpoints = {
    '/api/v1/datamesh/products/search': {
      status: 200,
      body: {
        total: 2,
        skip: 0,
        limit: 20,
        products: [
          {
            product_id: "retail-pos-transactions",
            product_name: "Retail POS Transactions",
            description: "Storefront and e-commerce transactions with real-time SCD2",
            owner_email: "pos-team@enterprise.com",
            domain_name: "RetailOperations",
            contract: {
              contract_id: "pos-v2.1.0",
              schema_version: "2.1.0",
              compliance_level: "confidential",
              sla: { freshness_hours: 1, availability_percent: 99.99 }
            },
            tags: ["retail", "transactions", "pii"]
          },
          {
            product_id: "airline-fleet-telemetry",
            product_name: "Airline Fleet Sensor Stream",
            description: "Aircraft engine metrics & mechanic maintenance logs",
            owner_email: "avionics@airline.com",
            domain_name: "AviationEngineering",
            contract: {
              contract_id: "fleet-v1.0.0",
              schema_version: "1.0.0",
              compliance_level: "internal"
            },
            tags: ["telemetry", "maintenance", "iot"]
          }
        ]
      }
    },
    '/api/v1/datamesh/governance/policies': {
      status: 200,
      body: {
        total: 4,
        policies: [
          {
            policy_id: "pii-detection-policy",
            policy_name: "PII Detection & Classification",
            scope: "global",
            enabled: true,
            enforcement_points: ["ingestion", "publication"],
            severity: "error"
          },
          {
            policy_id: "schema-drift-policy",
            policy_name: "Schema Drift Prevention",
            scope: "global",
            enabled: true,
            enforcement_points: ["ingestion", "transformation"],
            severity: "error"
          },
          {
            policy_id: "null-threshold-policy",
            policy_name: "Null Value Threshold Enforcement",
            scope: "global",
            enabled: true,
            enforcement_points: ["publication"],
            severity: "warn"
          },
          {
            policy_id: "data-retention-policy",
            policy_name: "Data Retention & Archival Enforcement",
            scope: "global",
            enabled: true,
            enforcement_points: ["publication"],
            severity: "warn"
          }
        ]
      }
    },
    '/api/v1/datamesh/governance/audit-trail': {
      status: 200,
      body: {
        total: 2,
        records: [
          {
            timestamp: "2026-08-23T13:45:00Z",
            product_id: "retail-pos-transactions",
            overall_decision: "allow",
            violations: []
          },
          {
            timestamp: "2026-08-23T12:10:22Z",
            product_id: "customer-analytics-raw",
            overall_decision: "deny",
            violations: ["PII field 'email' detected in PUBLIC compliance contract"]
          }
        ]
      }
    }
  };

  sendBtn.addEventListener('click', () => {
    apiResponse.innerHTML = '<span style="color: var(--cyan-primary);">Sending HTTP GET request...</span>';
    const path = apiEndpoint.value;
    const mock = mockEndpoints[path] || { status: 404, body: { error: "Not Found" } };

    setTimeout(() => {
      apiResponse.innerHTML = `
<span style="color: var(--emerald-primary); font-weight: 700;">HTTP/1.1 ${mock.status} OK</span>
<span style="color: var(--text-muted);">Content-Type: application/json</span>

${escapeHtml(JSON.stringify(mock.body, null, 2))}
      `.trim();
    }, 250);
  });
}

/* --------------------------------------------------------------------------
   8. Theme Toggle & Mobile Menu
   -------------------------------------------------------------------------- */
function initThemeToggle() {
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (!themeBtn) return;

  themeBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    themeBtn.innerHTML = newTheme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
  });
}

function initMobileMenu() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if (!menuBtn || !sidebar) return;

  menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  document.querySelectorAll('.sidebar .nav-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 1024) {
        sidebar.classList.remove('open');
      }
    });
  });
}

"""
Generate HTML report from validation suite results.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validation_suite.repo_paths import validation_suite_dir  # noqa: E402


def generate_report():
    suite_dir = validation_suite_dir()
    results_path = suite_dir / "results" / "master_results.json"
    if not results_path.exists():
        print("No results found. Run tests first.")
        return
    
    with open(results_path) as f:
        data = json.load(f)
    
    results = data.get("results", [])
    
    # Count verdicts
    verdicts = {}
    for r in results:
        v = r.get("verdict", "N/A")
        verdicts[v] = verdicts.get(v, 0) + 1
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARCHCODE Validation Suite Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #f8f9fa; color: #212529; line-height: 1.6; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; margin-bottom: 0.5rem; }}
        h2 {{ color: #16213e; margin: 2rem 0 1rem; border-bottom: 2px solid #0f3460; padding-bottom: 0.5rem; }}
        h3 {{ color: #1a1a2e; margin: 1.5rem 0 0.5rem; }}
        .subtitle {{ color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem; }}
        .card {{ background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; 
                 box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat {{ background: white; border-radius: 8px; padding: 1.5rem; text-align: center; 
                 box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2.5rem; font-weight: 700; }}
        .stat-label {{ color: #6c757d; font-size: 0.9rem; }}
        .verdict-PASS {{ color: #28a745; }}
        .verdict-WARNING {{ color: #ffc107; }}
        .verdict-FAIL {{ color: #dc3545; }}
        .verdict-SKIPPED {{ color: #6c757d; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th {{ background: #1a1a2e; color: white; padding: 0.75rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #dee2e6; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; 
                  font-size: 0.85rem; font-weight: 500; }}
        .badge-PASS {{ background: #d4edda; color: #155724; }}
        .badge-WARNING {{ background: #fff3cd; color: #856404; }}
        .badge-FAIL {{ background: #f8d7da; color: #721c24; }}
        .badge-SKIPPED {{ background: #e2e3e5; color: #383d41; }}
        .conclusion {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1.5rem; margin: 2rem 0; }}
        .conclusion h3 {{ color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 ARCHCODE Validation Suite Report</h1>
        <p class="subtitle">Falsification Framework for 3D-Genome Models — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <div class="summary-grid">
            <div class="stat">
                <div class="stat-number">{len(results)}</div>
                <div class="stat-label">Tests Run</div>
            </div>
            <div class="stat">
                <div class="stat-number verdict-PASS">{verdicts.get('PASS', 0)}</div>
                <div class="stat-label">PASS</div>
            </div>
            <div class="stat">
                <div class="stat-number verdict-WARNING">{verdicts.get('WARNING', 0)}</div>
                <div class="stat-label">WARNING</div>
            </div>
            <div class="stat">
                <div class="stat-number verdict-FAIL">{verdicts.get('FAIL', 0)}</div>
                <div class="stat-label">FAIL</div>
            </div>
        </div>
        
        <h2>Results by Test</h2>
        <table>
            <thead>
                <tr>
                    <th>Test</th>
                    <th>Locus</th>
                    <th>Status</th>
                    <th>Verdict</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for r in results:
        verdict = r.get("verdict", "N/A")
        badge = f'<span class="badge badge-{verdict}">{verdict}</span>'
        
        # Extract key details
        details = []
        if "ssim_auc" in r and r["ssim_auc"]:
            details.append(f"SSIM={r['ssim_auc']:.3f}")
        if "lr_auc" in r and r["lr_auc"]:
            details.append(f"LR={r['lr_auc']:.3f}")
        if "rf_auc" in r and r["rf_auc"]:
            details.append(f"RF={r['rf_auc']:.3f}")
        if "severity_auc" in r and r["severity_auc"]:
            details.append(f"Severity={r['severity_auc']:.3f}")
        if "median_within_cat_auc" in r:
            details.append(f"Med within-cat AUC={r['median_within_cat_auc']:.3f}")
        if "n_significant" in r:
            details.append(f"{r['n_significant']}/{r.get('n_categories_tested', '?')} cats sig.")
        if "shuffled_auc_median" in r:
            details.append(f"Shuffled AUC={r['shuffled_auc_median']:.3f}")
        
        details_str = ", ".join(details) if details else r.get("reason", "")
        
        html += f"""                <tr>
                    <td><strong>{r['test']}</strong></td>
                    <td>{r['locus']}</td>
                    <td>{r['status']}</td>
                    <td>{badge}</td>
                    <td>{details_str}</td>
                </tr>
"""
    
    html += """            </tbody>
        </table>
        
        <h2>Detailed Results</h2>
"""
    
    for r in results:
        if r["status"] != "COMPLETED":
            continue
        
        html += f"""        <div class="card">
            <h3>{r['test']} — {r['locus']}</h3>
            <p>Verdict: <span class="badge badge-{r.get('verdict', 'N/A')}">{r.get('verdict', 'N/A')}</span></p>
            <pre>{json.dumps({k: v for k, v in r.items() if k not in ['test', 'locus', 'status', 'verdict', 'category_results']}, indent=2)}</pre>
"""
        
        if "category_results" in r:
            html += """            <table>
                <thead><tr><th>Category</th><th>N(P/B)</th><th>AUC</th><th>Cohen's d</th><th>p-value</th><th>BH q-value</th><th>FDR</th></tr></thead>
                <tbody>
"""
            for cat in r["category_results"]:
                fdr_mark = "✅" if cat.get("survives_fdr") else ""
                bh_q_str = f"{cat['bh_q']:.4f}" if isinstance(cat.get('bh_q'), (int, float)) else "N/A"
                html += f"""                    <tr>
                        <td>{cat['category']}</td>
                        <td>{cat['n_pathogenic']}/{cat['n_benign']}</td>
                        <td>{cat['auc']:.3f}</td>
                        <td>{cat['cohens_d']:+.3f}</td>
                        <td>{cat['perm_p']:.4f}</td>
                        <td>{bh_q_str}</td>
                        <td>{fdr_mark}</td>
                    </tr>
"""
            html += """                </tbody>
            </table>
"""
        
        html += "        </div>\n"
    
    html += """
        <div class="conclusion">
            <h3>⚠️ Interpretation Guide</h3>
            <ul>
                <li><strong>PASS</strong> — ARCHCODE adds genuine value beyond simple baselines</li>
                <li><strong>WARNING</strong> — Signal exists but is fragile or marginal</li>
                <li><strong>FAIL</strong> — Simple baselines match or beat ARCHCODE; physics not justified for this task</li>
                <li><strong>SKIPPED</strong> — Insufficient data or configuration</li>
            </ul>
        </div>
        
        <footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 0.9rem;">
            <p>ARCHCODE Validation Suite v1.0 | Generated automatically from test results</p>
        </footer>
    </div>
</body>
</html>
"""
    
    report_path = suite_dir / "report.html"
    with open(report_path, "w") as f:
        f.write(html)
    
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    generate_report()

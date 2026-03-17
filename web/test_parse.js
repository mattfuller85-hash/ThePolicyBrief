import { marked } from 'marked';
import fs from 'fs';
const data = JSON.parse(fs.readFileSync('./src/data/daily_audits.json', 'utf8'));
const audit = data.find(d => d.bill_id === 'SRES434');
console.log(marked.parse(audit.blog_post_markdown || ''));

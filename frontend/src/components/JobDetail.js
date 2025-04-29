// src/components/JobDetail.js
import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

export default function JobDetail() {
  const { id }       = useParams();
  const navigate     = useNavigate();
  const [job, setJob]     = useState(null);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [form, setForm]   = useState({
    title: '',
    role: '',
    work_type: '',
    salary_range: '',
    description: '',
    responsibilities: '',
    qualifications: '',
    experience: '',
    preference: '',
    benefits: '',
  });

  const workTypeOptions = [
    'Intern','Temporary','Full-Time','Part-Time',
    'Contract','Remote','Hybrid'
  ];

  // 👉 load the job
  useEffect(() => {
    fetch(`/api/jobposting/${id}/`)
      .then(r => {
        if (!r.ok) throw new Error(`Status ${r.status}`);
        return r.json();
      })
      .then(data => {
        setJob(data);
        setForm({
          title: data.title,
          role: data.role,
          work_type: data.work_type,
          salary_range: data.salary_range,
          description: data.description,
          responsibilities: data.responsibilities,
          qualifications: data.qualifications,
          experience: data.experience,
          preference: data.preference,
          benefits: data.benefits,
        });
      })
      .catch(err => setError(err.message));
  }, [id]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSave = async e => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/jobposting/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error||res.statusText);
      }
  
      // 👉 refetch the updated record
      const fresh = await fetch(`/api/jobposting/${id}/`);
      const data  = await fresh.json();
      setJob(data);
      setEditMode(false);
  
    } catch (err) {
      setError(`Update failed: ${err.message}`);
    }
  };
  

  // 👉 delete job
  const handleDelete = async () => {
    if (!window.confirm('Delete this job forever?')) return;
    try {
      const res = await fetch(`/api/jobposting/${id}/`, { method: 'DELETE' });
      if (res.ok) return navigate('/');
      throw new Error(res.statusText);
    } catch (err) {
      setError(`Delete failed: ${err.message}`);
    }
  };

  if (error) return <p style={{ color:'red' }}>Error: {error}</p>;
  if (!job)   return <p>Loading…</p>;

  return (
    <div style={{ padding:'1rem' }}>
      <Link to="/" style={{ display:'block', marginBottom:'1rem' }}>
        ← Back to home
      </Link>

      {editMode ? (
        <form onSubmit={handleSave}>
          <h2>Edit Job</h2>

          <label>
            Title<br/>
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              required
            />
          </label><br/>

          <label>
            Role<br/>
            <input name="role" value={form.role} onChange={handleChange} />
          </label><br/>

          <label>
            Work Type<br/>
            <select
              name="work_type"
              value={form.work_type}
              onChange={handleChange}
              required
            >
              <option value="" disabled>Select one</option>
              {workTypeOptions.map(wt => (
                <option key={wt} value={wt}>{wt}</option>
              ))}
            </select>
          </label><br/>

          <label>
            Salary Range<br/>
            <input
              name="salary_range"
              value={form.salary_range}
              onChange={handleChange}
              required
            />
          </label><br/>

          <label>
            Description<br/>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
            />
          </label><br/>

          <label>
            Responsibilities<br/>
            <textarea
              name="responsibilities"
              value={form.responsibilities}
              onChange={handleChange}
            />
          </label><br/>

          <label>
            Qualifications<br/>
            <textarea
              name="qualifications"
              value={form.qualifications}
              onChange={handleChange}
            />
          </label><br/>

          <label>
            Experience<br/>
            <textarea
              name="experience"
              value={form.experience}
              onChange={handleChange}
            />
          </label><br/>

          <label>
            Preference<br/>
            <textarea
              name="preference"
              value={form.preference}
              onChange={handleChange}
            />
          </label><br/>

          <label>
            Benefits<br/>
            <textarea
              name="benefits"
              value={form.benefits}
              onChange={handleChange}
            />
          </label><br/>

          <button type="submit" style={{ marginRight:'1rem' }}>💾 Save</button>
          <button type="button" onClick={() => setEditMode(false)}>
            ✖️ Cancel
          </button>
        </form>
      ) : (
        <>
          <h1>{job.title}</h1>
          <p><strong>Company:</strong> {job.company_name}</p>
          <p><strong>Posted on:</strong> {job.posting_date}</p>
          <p><strong>Role:</strong> {job.role || '—'}</p>
          <p><strong>Work Type:</strong> {job.work_type}</p>
          <p><strong>Salary:</strong> {job.salary_range}</p>
          <hr/>
          <p><strong>Description:</strong><br/>{job.description || '—'}</p>
          <p><strong>Responsibilities:</strong><br/>{job.responsibilities || '—'}</p>
          <p><strong>Qualifications:</strong><br/>{job.qualifications || '—'}</p>
          <p><strong>Experience:</strong><br/>{job.experience || '—'}</p>
          <p><strong>Preference:</strong><br/>{job.preference || '—'}</p>
          <p><strong>Benefits:</strong><br/>{job.benefits || '—'}</p>

          <div style={{ marginTop:'1.5rem' }}>
            <button
              onClick={() => setEditMode(true)}
              style={{ marginRight:'1rem' }}
            >
              ✏️ Edit
            </button>
            <button
              onClick={handleDelete}
              style={{
                background:'tomato',
                color:'#fff',
                border:'none',
                padding:'0.5rem 1rem',
                borderRadius:'4px',
                cursor:'pointer'
              }}
            >
              🗑️ Delete
            </button>
          </div>
        </>
      )}
    </div>
  );
}

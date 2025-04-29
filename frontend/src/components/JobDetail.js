// src/components/JobDetail.js
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);

  useEffect(() => {
    fetch(`/api/jobposting/${id}/`)
      .then(r => {
        if (!r.ok) throw new Error(`Status ${r.status}`);
        return r.json();
      })
      .then(setJob)
      .catch(err => {
        console.error(err);
        setJob({ error: err.message });
      });
  }, [id]);

  if (!job) return <p>Loading job…</p>;
  if (job.error) return <p>Error: {job.error}</p>;

  return (
    <div style={{ padding: '1rem' }}>
      <Link to="/" style={{ display: 'block', marginBottom: '1rem' }}>
        ← Back to home
      </Link>

      <h1>{job.title}</h1>
      <p>
        <strong>Company:</strong>{' '}
        <Link to={`/company/${job.company_id}`}>
          {job.company_name}
        </Link>
      </p>
      <p><strong>Role:</strong> {job.role || '—'}</p>
      <p><strong>Work Type:</strong> {job.work_type}</p>
      <p><strong>Salary Range:</strong> {job.salary_range}</p>
      <p>
        <strong>Location:</strong> {job.location_city}, {job.location_country}
      </p>
      <p><strong>Posted on:</strong> {job.posting_date}</p>
      <hr />

      <p><strong>Description:</strong><br />{job.description || '—'}</p>
      <p><strong>Responsibilities:</strong><br />{job.responsibilities || '—'}</p>
      <p><strong>Qualifications:</strong><br />{job.qualifications || '—'}</p>
      <p><strong>Experience:</strong><br />{job.experience || '—'}</p>
      <p><strong>Preference:</strong><br />{job.preference || '—'}</p>
      <p><strong>Benefits:</strong><br />{job.benefits || '—'}</p>

      {job.skills && job.skills.length > 0 && (
        <>
          <hr />
          <strong>Skills:</strong>
          <ul>
            {job.skills.map(s => (
              <li key={s.id}>{s.name}</li>
            ))}
          </ul>
        </>
      )}

      {job.job_portal_id && (
        <p>
          <strong>Posted via portal #:</strong> {job.job_portal_id}
        </p>
      )}
    </div>
  );
}

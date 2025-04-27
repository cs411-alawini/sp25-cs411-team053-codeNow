// src/components/CreateJobForm.js
import React, { useState, useEffect } from 'react';

export default function CreateJobForm({ onSuccess }) {
  const workTypeOptions = [
    'Intern',
    'Temporary',
    'Full-Time',
    'Part-Time',
    'Contract',
    'Remote',
    'Hybrid',
  ];

  const [form, setForm] = useState({
    title: '',
    role: '',
    work_type: '',
    salary_range: '',
    company_name: '',
    city: '',
    country: '',
    job_portal_id: '',
    skills: [],        // now an actual array
    description: '',
    responsibilities: '',
    qualifications: '',
    experience: '',
    preference: '',
    benefits: '',
  });
  const [skillsList, setSkillsList]     = useState([]);
  const [portalsList, setPortalsList]   = useState([]);
  const [error, setError]               = useState('');

  // Fetch skills & portals once
  useEffect(() => {
    fetch('/api/skills/')
      .then(r => r.json())
      .then(setSkillsList)
      .catch(console.error);

    fetch('/api/jobportals/')
      .then(r => r.json())
      .then(setPortalsList)
      .catch(console.error);
  }, []);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleMultiChange = e => {
    const opts = Array.from(e.target.selectedOptions);
    const vals = opts
      .map(o => parseInt(o.value, 10))
      .filter(n => !isNaN(n));
    setForm(prev => ({ ...prev, skills: vals }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    // payload is exactly your form object
    const payload = { ...form };

    try {
      const res = await fetch('/api/jobposting/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || res.statusText);

      alert(`✅ Created! PK=${json.created_id}, job_id=${json.job_id}`);
      onSuccess && onSuccess(json.created_id);

      // reset to initial state
      setForm({
        title: '',
        role: '',
        work_type: '',
        salary_range: '',
        company_name: '',
        city: '',
        country: '',
        job_portal_id: '',
        skills: [],
        description: '',
        responsibilities: '',
        qualifications: '',
        experience: '',
        preference: '',
        benefits: '',
      });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="create-job-form" onSubmit={handleSubmit}>
      {error && <p className="error">{error}</p>}

      <input
        name="title"
        value={form.title}
        onChange={handleChange}
        placeholder="Title"
        required
      />

      <input
        name="role"
        value={form.role}
        onChange={handleChange}
        placeholder="Role"
      />

      <select
        name="work_type"
        value={form.work_type}
        onChange={handleChange}
        required
      >
        <option value="" disabled>
          Select Work Type
        </option>
        {workTypeOptions.map(type => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </select>

      <input
        name="salary_range"
        value={form.salary_range}
        onChange={handleChange}
        placeholder="Salary Range"
        required
      />

      <input
        name="company_name"
        value={form.company_name}
        onChange={handleChange}
        placeholder="Company Name"
        required
      />

      <input
        name="city"
        value={form.city}
        onChange={handleChange}
        placeholder="City"
        required
      />

      <input
        name="country"
        value={form.country}
        onChange={handleChange}
        placeholder="Country"
        required
      />

      <select
        name="job_portal_id"
        value={form.job_portal_id}
        onChange={handleChange}
      >
        <option value="">Select Job Portal (opt)</option>
        {portalsList.map(p => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </select>

      <label>Skills (ctrl+click to multi-select):</label>
      <select
        name="skills"
        multiple
        value={form.skills}
        onChange={handleMultiChange}
        size={Math.min(5, skillsList.length)}
      >
        {skillsList.map(s => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>

      <textarea
        name="description"
        value={form.description}
        onChange={handleChange}
        placeholder="Description"
      />
      <textarea
        name="responsibilities"
        value={form.responsibilities}
        onChange={handleChange}
        placeholder="Responsibilities"
      />
      <textarea
        name="qualifications"
        value={form.qualifications}
        onChange={handleChange}
        placeholder="Qualifications"
      />
      <textarea
        name="experience"
        value={form.experience}
        onChange={handleChange}
        placeholder="Experience"
      />
      <textarea
        name="preference"
        value={form.preference}
        onChange={handleChange}
        placeholder="Preference"
      />
      <textarea
        name="benefits"
        value={form.benefits}
        onChange={handleChange}
        placeholder="Benefits"
      />

      <button type="submit">Create Job 🚀</button>
    </form>
  );
}

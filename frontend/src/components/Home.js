// src/components/Home.js
import React, { useState }    from 'react';
import { Link }               from 'react-router-dom';
import CreateJobForm          from './CreateJobForm';
import Header                 from './Header';

// add onSearch & searchResults props:
export default function Home({
  recentPosting,
  searchResults,
  onSearch,
  showForm,
  setShowForm,
  onCreated
}) {
  const [term, setTerm] = useState('');

  const handleSubmit = e => {
    e.preventDefault();
    onSearch(term.trim());
  };

  // choose which list to show
  const listToShow = searchResults !== null
    ? searchResults
    : recentPosting;

  return (
    <div>
      <Header />

      {/* search bar */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <input
          value={term}
          onChange={e => setTerm(e.target.value)}
          placeholder="Search jobs…"
        />
        <button type="submit">Search</button>
        {searchResults !== null && (
          <button type="button" onClick={() => {
            setTerm('');
            onSearch('');
          }}>✖️ Clear</button>
        )}
      </form>

      {/* create‐job form */}
      <button onClick={() => setShowForm(f => !f)}>
        {showForm ? '✖️ Cancel' : '➕ Create Job Posting'}
      </button>
      {showForm && <CreateJobForm onSuccess={onCreated} />}

      {/* results (either search or recent) */}
      <h1>
        {searchResults !== null
          ? `Search results for “${term}”:`
          : 'Recent Job Postings'}
      </h1>
      <div>
        {listToShow.length === 0
          ? <p>No jobs to display.</p>
          : listToShow.map(p => (
              <div key={p.id} style={{ padding: '0.5rem 0' }}>
                <Link to={`/job/${p.id}`}><strong>{p.title}</strong></Link>
                {' from '}
                <Link to={`/company/${p.company_id}`}>
                  {p.company_name || `Company #${p.company_id}`}
                </Link>
                { searchResults===null && <span> — {p.posting_date}</span> }
              </div>
            ))
        }
      </div>
    </div>
  );
}

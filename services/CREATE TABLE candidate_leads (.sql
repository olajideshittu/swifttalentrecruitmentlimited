CREATE TABLE candidate_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT,
    title TEXT,
    location TEXT,
    linkedin_url TEXT UNIQUE,
    phone_number TEXT,
    match_score DECIMAL,
    outreach_status TEXT DEFAULT 'pending' -- pending, contacted, interested, rejected
);

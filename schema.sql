-- Supabase Schema for GAD Application
-- Run this in the SQL Editor (https://supabase.com/dashboard/project/jheomrhrufzslklasnuy/sql/new)

-- 1. Events Table
create table if not exists public.events (
    id text primary key,
    date date not null,
    title text not null,
    category text,
    description text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. Projects Table
create table if not exists public.projects (
    id text primary key,
    year integer not null,
    title text not null,
    category text,
    description text,
    status text,
    image text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Policies Table
create table if not exists public.policies (
    id text primary key,
    category text not null,
    year integer not null,
    title text not null,
    description text,
    date text,
    status text,
    file text,
    url text,
    video_file text,
    video_url text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 4. Knowledge Products Table
create table if not exists public.knowledge_products (
    id text primary key,
    title text not null,
    description text,
    type text,
    date text,
    image text,
    file text,
    url text,
    action_text text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 5. Brochures Table
create table if not exists public.brochures (
    id text primary key,
    title text not null,
    url text,
    file text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 6. Tracking Matrix Table
create table if not exists public.tracking_matrix (
    id text primary key,
    corner text,
    date text,
    time_started text,
    time_completed text,
    type text,
    description text,
    updates_posted text,
    technical_officer text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 7. Livelihood Feeds Table
create table if not exists public.livelihood_feeds (
    id text primary key,
    title text not null,
    description text,
    type text,
    url text,
    file text,
    date text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 8. Committee Members Table
create table if not exists public.committee (
    id text primary key,
    name text not null,
    position text,
    role text,
    image text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 9. Org Structure Table
create table if not exists public.org_structure (
    id text primary key default 'singleton',
    chart_image text,
    pdf_url text,
    manual_url text,
    components jsonb,
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- 10. Carousel Images Table
create table if not exists public.carousel (
    id serial primary key,
    url text not null,
    display_order integer default 0,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 11. News Table
create table if not exists public.news (
    id text primary key,
    title text not null,
    content text,
    date text,
    author text,
    image text,
    url text,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- --- Enable RLS and Set Policies ---

alter table public.events enable row level security;
alter table public.projects enable row level security;
alter table public.policies enable row level security;
alter table public.knowledge_products enable row level security;
alter table public.brochures enable row level security;
alter table public.tracking_matrix enable row level security;
alter table public.livelihood_feeds enable row level security;
alter table public.committee enable row level security;
alter table public.org_structure enable row level security;
alter table public.carousel enable row level security;
alter table public.news enable row level security;

-- DROP EXISTING POLICIES (if any) TO ALLOW RE-RUN
do $$ 
begin
    execute 'drop policy if exists "Public full access for events" on public.events';
    execute 'drop policy if exists "Public full access for projects" on public.projects';
    execute 'drop policy if exists "Public full access for policies" on public.policies';
    execute 'drop policy if exists "Public full access for knowledge_products" on public.knowledge_products';
    execute 'drop policy if exists "Public full access for brochures" on public.brochures';
    execute 'drop policy if exists "Public full access for tracking_matrix" on public.tracking_matrix';
    execute 'drop policy if exists "Public full access for livelihood_feeds" on public.livelihood_feeds';
    execute 'drop policy if exists "Public full access for committee" on public.committee';
    execute 'drop policy if exists "Public full access for org_structure" on public.org_structure';
    execute 'drop policy if exists "Public full access for carousel" on public.carousel';
    execute 'drop policy if exists "Public full access for news" on public.news';
exception when others then null;
end $$;
-- 12. Site Config Table
create table if not exists public.site_config (
    id text primary key default 'singleton',
    config jsonb,
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Enable RLS
alter table public.site_config enable row level security;
            
-- Policies
create policy "Public full access for site_config" on public.site_config for all using (true);

-- Policies for public access (Temporary for migration)
create policy "Public full access for events" on public.events for all using (true);
create policy "Public full access for projects" on public.projects for all using (true);
create policy "Public full access for policies" on public.policies for all using (true);
create policy "Public full access for knowledge_products" on public.knowledge_products for all using (true);
create policy "Public full access for brochures" on public.brochures for all using (true);
create policy "Public full access for tracking_matrix" on public.tracking_matrix for all using (true);
create policy "Public full access for livelihood_feeds" on public.livelihood_feeds for all using (true);
create policy "Public full access for committee" on public.committee for all using (true);
create policy "Public full access for org_structure" on public.org_structure for all using (true);
create policy "Public full access for carousel" on public.carousel for all using (true);
create policy "Public full access for news" on public.news for all using (true);

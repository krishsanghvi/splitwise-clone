-- =====================================================
-- SPLITFLOW - SQL SCHEMA MATCHING PYTHON MODELS
-- No Currency Support (USD Only)
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- CREATE CUSTOM TYPES (ENUMS)
-- =====================================================

CREATE TYPE user_role AS ENUM ('admin', 'member');
CREATE TYPE split_method AS ENUM ('equal', 'exact', 'percentage', 'shares');
CREATE TYPE settlement_method AS ENUM ('cash', 'venmo', 'paypal', 'bank_transfer', 'zelle', 'cashapp', 'other');

-- =====================================================
-- CREATE TABLES MATCHING PYTHON MODELS
-- =====================================================

-- USERS TABLE (matches users.py)
CREATE TABLE public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  timezone TEXT DEFAULT 'UTC',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CATEGORIES TABLE (matches categories.py)
CREATE TABLE public.categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  icon TEXT NOT NULL,
  color TEXT NOT NULL,
  is_default BOOLEAN DEFAULT false
);

-- GROUPS TABLE (matches groups.py)
CREATE TABLE public.groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  group_name TEXT NOT NULL,  -- matches your field name
  group_description TEXT,    -- matches your field name
  invite_code TEXT UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(6), 'base64'),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- GROUP_MEMBERS TABLE (matches group_members.py)
CREATE TABLE public.group_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id UUID NOT NULL REFERENCES public.groups(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  role user_role NOT NULL DEFAULT 'member',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true,
  
  -- Ensure one membership per user per group
  UNIQUE(group_id, user_id)
);

-- EXPENSES TABLE (you have empty expenses.py - here's what it should be)
CREATE TABLE public.expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id UUID NOT NULL REFERENCES public.groups(id) ON DELETE CASCADE,
  paid_by UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
  amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
  description TEXT NOT NULL,
  receipt_url TEXT,
  notes TEXT,
  split_method split_method NOT NULL DEFAULT 'equal',
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- EXPENSE_SHARES TABLE (matches expense_shares.py - with typo fix)
CREATE TABLE public.expense_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  expense_id UUID NOT NULL REFERENCES public.expenses(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  amount_owed DECIMAL(12,2) NOT NULL CHECK (amount_owed >= 0), -- Fixed your typo: amount_owned -> amount_owed
  is_settled BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- One share per user per expense
  UNIQUE(expense_id, user_id)
);

-- BALANCES TABLE (matches balances.py)
CREATE TABLE public.balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id UUID NOT NULL REFERENCES public.groups(id) ON DELETE CASCADE,
  user_from UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  user_to UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  amount DECIMAL(12,2) NOT NULL DEFAULT 0,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  
  -- Prevent self-balances and ensure unique pairs
  CHECK (user_from != user_to),
  UNIQUE(group_id, user_from, user_to)
);

-- SETTLEMENTS TABLE (not in your Python models but essential)
CREATE TABLE public.settlements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id UUID NOT NULL REFERENCES public.groups(id) ON DELETE CASCADE,
  from_user UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  to_user UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
  method settlement_method DEFAULT 'cash',
  reference_id TEXT,
  notes TEXT,
  settled_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CHECK (from_user != to_user)
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Users indexes
CREATE INDEX idx_users_email ON public.users(email);

-- Categories indexes  
CREATE INDEX idx_categories_is_default ON public.categories(is_default) WHERE is_default = true;

-- Groups indexes
CREATE INDEX idx_groups_invite_code ON public.groups(invite_code);
CREATE INDEX idx_groups_created_by ON public.groups(created_by);
CREATE INDEX idx_groups_active ON public.groups(is_active) WHERE is_active = true;

-- Group Members indexes (Critical for permission checks)
CREATE INDEX idx_group_members_group_id ON public.group_members(group_id);
CREATE INDEX idx_group_members_user_id ON public.group_members(user_id);
CREATE INDEX idx_group_members_active ON public.group_members(group_id, user_id) WHERE is_active = true;

-- Expenses indexes (Most queried table)
CREATE INDEX idx_expenses_group_id ON public.expenses(group_id);
CREATE INDEX idx_expenses_paid_by ON public.expenses(paid_by);
CREATE INDEX idx_expenses_date ON public.expenses(expense_date DESC);
CREATE INDEX idx_expenses_group_date ON public.expenses(group_id, expense_date DESC);
CREATE INDEX idx_expenses_category ON public.expenses(category_id);

-- Expense Shares indexes (For balance calculations)
CREATE INDEX idx_expense_shares_expense_id ON public.expense_shares(expense_id);
CREATE INDEX idx_expense_shares_user_id ON public.expense_shares(user_id);
CREATE INDEX idx_expense_shares_unsettled ON public.expense_shares(user_id, is_settled) WHERE is_settled = false;

-- Balances indexes (Frequently queried for debt overview)
CREATE INDEX idx_balances_group_id ON public.balances(group_id);
CREATE INDEX idx_balances_user_from ON public.balances(user_from);
CREATE INDEX idx_balances_user_to ON public.balances(user_to);
CREATE INDEX idx_balances_nonzero ON public.balances(group_id) WHERE amount != 0;

-- Settlements indexes
CREATE INDEX idx_settlements_group_id ON public.settlements(group_id);
CREATE INDEX idx_settlements_from_user ON public.settlements(from_user);
CREATE INDEX idx_settlements_to_user ON public.settlements(to_user);
CREATE INDEX idx_settlements_date ON public.settlements(settled_at DESC);

-- =====================================================
-- INSERT DEFAULT CATEGORIES
-- =====================================================

INSERT INTO public.categories (name, icon, color, is_default) VALUES
('Food & Drinks', '🍕', '#FF6B6B', true),
('Transportation', '🚗', '#4ECDC4', true),
('Accommodation', '🏠', '#45B7D1', true),
('Entertainment', '🎬', '#96CEB4', true),
('Shopping', '🛒', '#FFEAA7', true),
('Utilities', '⚡', '#DDA0DD', true),
('Healthcare', '🏥', '#FD79A8', true),
('Education', '📚', '#A29BFE', true),
('Travel', '✈️', '#00B894', true),
('Other', '📋', '#95A5A6', true);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expense_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settlements ENABLE ROW LEVEL SECURITY;

-- USERS TABLE POLICIES
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view group members" ON public.users
  FOR SELECT USING (
    id IN (
      SELECT DISTINCT gm2.user_id 
      FROM public.group_members gm1
      JOIN public.group_members gm2 ON gm1.group_id = gm2.group_id
      WHERE gm1.user_id = auth.uid() AND gm1.is_active = true AND gm2.is_active = true
    )
  );

-- GROUPS TABLE POLICIES
CREATE POLICY "Users can view their groups" ON public.groups
  FOR SELECT USING (
    id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    )
  );

CREATE POLICY "Authenticated users can create groups" ON public.groups
  FOR INSERT WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Group admins can update groups" ON public.groups
  FOR UPDATE USING (
    id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND role = 'admin' AND is_active = true
    )
  );

-- GROUP_MEMBERS TABLE POLICIES
CREATE POLICY "Users can view group members" ON public.group_members
  FOR SELECT USING (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    )
  );

CREATE POLICY "Group admins can manage members" ON public.group_members
  FOR ALL USING (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND role = 'admin' AND is_active = true
    )
  );

-- EXPENSES TABLE POLICIES
CREATE POLICY "Users can view group expenses" ON public.expenses
  FOR SELECT USING (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    )
  );

CREATE POLICY "Users can add expenses to their groups" ON public.expenses
  FOR INSERT WITH CHECK (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    ) AND paid_by = auth.uid()
  );

CREATE POLICY "Users can update own expenses" ON public.expenses
  FOR UPDATE USING (paid_by = auth.uid());

-- EXPENSE_SHARES TABLE POLICIES
CREATE POLICY "Users can view expense shares" ON public.expense_shares
  FOR SELECT USING (
    expense_id IN (
      SELECT id FROM public.expenses
      WHERE group_id IN (
        SELECT group_id FROM public.group_members 
        WHERE user_id = auth.uid() AND is_active = true
      )
    )
  );

-- BALANCES TABLE POLICIES
CREATE POLICY "Users can view group balances" ON public.balances
  FOR SELECT USING (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    )
  );

-- SETTLEMENTS TABLE POLICIES
CREATE POLICY "Users can view group settlements" ON public.settlements
  FOR SELECT USING (
    group_id IN (
      SELECT group_id FROM public.group_members 
      WHERE user_id = auth.uid() AND is_active = true
    )
  );

CREATE POLICY "Users can create settlements" ON public.settlements
  FOR INSERT WITH CHECK (from_user = auth.uid() OR to_user = auth.uid());

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at 
  BEFORE UPDATE ON public.users 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_groups_updated_at 
  BEFORE UPDATE ON public.groups 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at 
  BEFORE UPDATE ON public.expenses 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- USER ONBOARDING TRIGGER
-- =====================================================

-- Function to create user profile when they sign up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- =====================================================
-- ENABLE REALTIME FOR LIVE UPDATES
-- =====================================================

ALTER PUBLICATION supabase_realtime ADD TABLE public.expenses;
ALTER PUBLICATION supabase_realtime ADD TABLE public.expense_shares;
ALTER PUBLICATION supabase_realtime ADD TABLE public.balances;
ALTER PUBLICATION supabase_realtime ADD TABLE public.settlements;
ALTER PUBLICATION supabase_realtime ADD TABLE public.group_members;
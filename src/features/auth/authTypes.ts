export type AuthRole =
  | "Member"
  | "Mentor"
  | "Moderator"
  | "Case Handler"
  | "Organisation Administrator"
  | "Programme Administrator";

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  role: AuthRole;
  institution_id: number | null;
  institution_name: string | null;
  is_active: boolean;
};

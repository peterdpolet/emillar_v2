export interface User {
  id:           number
  email:        string
  first_name:   string
  last_name:    string
  totp_enabled: boolean
  role:         'staff' | 'customer' | 'supplier'
}

export interface RegisterData {
  email:       string
  password:    string
  re_password: string
  first_name?: string
  last_name?:  string
}

export interface LoginData {
  email:    string
  password: string
}

export interface LoginResponse {
  access:         string
  refresh:        string
  totp_required?: boolean
  uid?:           string
}

export interface TokenResponse {
  access:   string
  refresh?: string
}
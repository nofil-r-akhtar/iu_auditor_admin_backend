from app.config.database import supabase

# Test 1 - fetch all users
result = supabase.table("users").select("*").execute()
print("All users:", result.data)

# Test 2 - fetch by email
result2 = supabase.table("users").select("*").eq("email", "nofilraheel1@gmail.com").execute()
print("Specific user:", result2.data)
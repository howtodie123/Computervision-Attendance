using Microsoft.EntityFrameworkCore;
using Server.Model;
using System.Net;

namespace Server.Data
{
    public class APIData : DbContext
    {
        public APIData(DbContextOptions options) : base(options)
        {
        }
        public DbSet<Adduser> adduser { get; set; }
        public DbSet<DeleteUser> deleteuser { get; set; }
        public DbSet<Attendance> attendance { get; set; }
        public DbSet<LogDeleteAdd> logdeleteadd { get; set; }
    }
}
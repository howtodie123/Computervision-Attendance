using Microsoft.AspNetCore.Mvc;
using Server.Model;
using Microsoft.EntityFrameworkCore;
using Server.Data;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

namespace Server.Controllers
{
    [ApiController]
    [Route("api/attendance")]
    public class AttendanceController : Controller
    {
        private readonly APIData dbContext;
        private readonly IConfiguration _configuration;

        public AttendanceController(APIData dbContext, IConfiguration _configuration)
        {
            this.dbContext = dbContext;
            this._configuration = _configuration;
        }
        // get: lấy dữ liệu
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            return Ok(await dbContext.attendance.ToListAsync());
        }
        
        [HttpGet]
        [Route("{id:int}")]
        public async Task<IActionResult> GetOne([FromRoute] int id)
        {
            var add = await dbContext.attendance.FindAsync(id);
            if (add == null) { return NotFound(); }
            return Ok(add);
        }
        // post: tạo data mới
        [HttpPost]
        public async Task<IActionResult> Add(RequestAttendance request)
        {
            string check1 ;
            string check2 ;
            int a = 0;
            var att = new Attendance();
           await
           using (var connection = new SqlConnection(_configuration.GetConnectionString("ApiDatabase")))
            {
                var sql = "SELECT DAYCHECK, IDUSER FROM Attendance Where IDUSER = '" + request.IDUSER.ToString() + "'";
                connection.Open();
                using SqlCommand command = new SqlCommand(sql, connection);
                using SqlDataReader reader = command.ExecuteReader();
                while (reader.Read())
                {
                    check1 = reader["DAYCHECK"].ToString();
                    check2 = reader["IDUSER"].ToString();
                    if(check2 == request.IDUSER && check1 == request.DAYCHECK)
                    {
                        a += 1;
                    }
                         
                }
                reader.Close();
            }

            if (a > 0)
            {
                a = 0;
                return Ok(att);
            }
            var att2 = new Attendance()
            {
                IDUSER = request.IDUSER,
                LOGATT = request.LOGATT,
                DAYCHECK = request.DAYCHECK
            };
            await dbContext.attendance.AddAsync(att2);
            await dbContext.SaveChangesAsync();
            a = 0;
            return Ok(att2);
        }
    }
}

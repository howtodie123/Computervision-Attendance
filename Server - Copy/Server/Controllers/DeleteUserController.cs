using Microsoft.AspNetCore.Mvc;
using Server.Model;
using Microsoft.EntityFrameworkCore;
using Server.Data;
using Microsoft.Data.SqlClient;
using static Microsoft.EntityFrameworkCore.DbLoggerCategory.Database;
using Microsoft.Extensions.Configuration;

namespace Server.Controllers
{
    [ApiController]
    [Route("api/deleteuser")]
    public class DeleteUserController : Controller
    {
        private readonly APIData dbContext;
        private readonly IConfiguration _configuration;

        public DeleteUserController(APIData dbContext, IConfiguration _configuration)
        {
            this.dbContext = dbContext;
            this._configuration = _configuration;

        }
        // get: lấy dữ liệu
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            return Ok(await dbContext.deleteuser.ToListAsync());
        }
        
        [HttpGet]
        [Route("{id:int}")]
        public async Task<IActionResult> GetOne([FromRoute] int id)
        {
            var add = await dbContext.deleteuser.FindAsync(id);
            if (add == null) { return NotFound(); }
            return Ok(add);
        }
        // post: tạo data mới
        [HttpPost]
        public async Task<IActionResult> Add(RequestUser request)
        {
            var deleteUser = new DeleteUser();

            // Xóa user trong bảng add user
            await
            using (var connection = new SqlConnection(_configuration.GetConnectionString("ApiDatabase")))
            {
                var sql = "SELECT DATEJOIN FROM AddUser Where IDUSER = '" + request.IDUSER.ToString() + "'";
                connection.Open();
                using SqlCommand command = new SqlCommand(sql, connection);
                using SqlDataReader reader = command.ExecuteReader();
                while (reader.Read())
                {
                    // thêm user đã xóa vào bảng deleteUser
                    var deleteUser1 = new DeleteUser()
                    {
                        IDUSER = request.IDUSER,
                        NAMEUSER = request.NAMEUSER,
                        DATEJOIN = reader["DATEJOIN"].ToString(),
                        DATEOUT = request.DATEOUT,
                    };
                    await dbContext.deleteuser.AddAsync(deleteUser1);
                    await dbContext.SaveChangesAsync();
                    deleteUser = deleteUser1;
                }
                reader.Close();
                var sqlDelete= "Delete FROM AddUser WHERE IDUSER = '" + request.IDUSER.ToString() + "'";
                using SqlCommand sqlCommand = new SqlCommand(sqlDelete, connection);
                SqlDataReader sqlReader = sqlCommand.ExecuteReader();
                sqlReader.Close();
            }

            LogDeleteAdd log1 = new LogDeleteAdd();
            log1.LOGDA = "The User Name: " +request.NAMEUSER + " has deleted at: " + request.DATEOUT ;
            await dbContext.logdeleteadd.AddAsync(log1);
            await dbContext.SaveChangesAsync();
            return Ok(deleteUser);
        }
    }
}

using Microsoft.AspNetCore.Mvc;
using Server.Model;
using Microsoft.EntityFrameworkCore;
using Server.Data;
using Microsoft.Data.SqlClient;

namespace Server.Controllers
{
    [ApiController]
    [Route("api/LogDeleteAdduser")]
    public class LogDeleteAddUserController : Controller
    {
        private readonly APIData dbContext;

        public LogDeleteAddUserController(APIData dbContext)
        {
            this.dbContext = dbContext;
        }
        // get: lấy dữ liệu
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            return Ok(await dbContext.logdeleteadd.ToListAsync());
        }
        
        [HttpGet]
        [Route("{id:int}")]
        public async Task<IActionResult> GetOne([FromRoute] int id)
        {
            var add = await dbContext.logdeleteadd.FindAsync(id);
            if (add == null) { return NotFound(); }
            return Ok(add);
        }
        // post: tạo data mới
        [HttpPost]
        public async Task<IActionResult> Add(Adduser request)
        {
            var adduser = new Adduser()
            {
                IDUSER = request.IDUSER,
                NAMEUSER = request.NAMEUSER,
                DATEJOIN = request.DATEJOIN,
                DATEOUT = request.DATEOUT,
            };
            
            await dbContext.adduser.AddAsync(adduser);
            await dbContext.SaveChangesAsync();

            // Thay đổi giá trị trong LogDeleteAdd

            LogDeleteAdd log1 = new LogDeleteAdd();
            log1.LOGDA = "The User Name: " +request.NAMEUSER + "has add at: " + request.DATEJOIN ;
            await dbContext.logdeleteadd.AddAsync(log1);

            return Ok(adduser);
        }
    }
}

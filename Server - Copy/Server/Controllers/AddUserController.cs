using Microsoft.AspNetCore.Mvc;
using Server.Model;
using Microsoft.EntityFrameworkCore;
using Server.Data;
using Microsoft.Data.SqlClient;

namespace Server.Controllers
{
    [ApiController]
    [Route("api/adduser")]
    public class AddUserController : Controller
    {
        private readonly APIData dbContext;

        public AddUserController(APIData dbContext)
        {
            this.dbContext = dbContext;
        }
        // get: lấy dữ liệu
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            return Ok(await dbContext.adduser.ToListAsync());
        }
        
        [HttpGet]
        [Route("{id:int}")]
        public async Task<IActionResult> GetOne([FromRoute] int id)
        {
            var add = await dbContext.adduser.FindAsync(id);
            if (add == null) { return NotFound(); }
            return Ok(add);
        }
        // post: tạo data mới
        [HttpPost]
        public async Task<IActionResult> Add(RequestUser request)
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

            // Thêm giá trị trong LogDeleteAdd

            LogDeleteAdd log1 = new LogDeleteAdd();
            log1.LOGDA = "The User Name: " +request.NAMEUSER + " has add at: " + request.DATEJOIN ;
            await dbContext.logdeleteadd.AddAsync(log1);
            await dbContext.SaveChangesAsync();
            // Thêm giá trị attendance
            return Ok(adduser);
        }
        [HttpDelete]
        [Route("{id:int}")]
        public async Task<IActionResult> Delete([FromRoute] int id)
        {
            var admin = await dbContext.adduser.FindAsync(id);
            if (admin != null)
            {
                dbContext.Remove(admin);
                await dbContext.SaveChangesAsync();
                return Ok(admin);
            }
            return NotFound();
        }
    }
}
